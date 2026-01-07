import pytest
from app import app, clear_tasks


@pytest.fixture(autouse=True)
def _clear_store_between_tests():
    clear_tasks()
    yield
    clear_tasks()


def test_home():
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.get_json()["message"]


def test_health():
    client = app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_create_task_returns_201_and_task_shape():
    client = app.test_client()
    resp = client.post("/tasks", json={"name": "backup-db", "payload": {"db": "prod"}})
    assert resp.status_code == 201

    task = resp.get_json()
    assert isinstance(task["id"], str) and task["id"]
    assert task["name"] == "backup-db"
    assert task["status"] == "pending"
    assert task["payload"] == {"db": "prod"}
    assert task["result"] is None
    assert task["error"] is None
    assert "created_at" in task
    assert "updated_at" in task


def test_create_task_requires_name():
    client = app.test_client()
    resp = client.post("/tasks", json={"payload": {"x": 1}})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_list_tasks_contains_created_task():
    client = app.test_client()
    create = client.post("/tasks", json={"name": "task-1"})
    task_id = create.get_json()["id"]

    resp = client.get("/tasks")
    assert resp.status_code == 200
    tasks = resp.get_json()
    assert any(t["id"] == task_id for t in tasks)


def test_get_task_returns_404_for_unknown_id():
    client = app.test_client()
    resp = client.get("/tasks/not-a-real-id")
    assert resp.status_code == 404


def test_update_task_status_running_then_done():
    client = app.test_client()
    created = client.post("/tasks", json={"name": "compile"})
    task_id = created.get_json()["id"]

    running = client.patch(f"/tasks/{task_id}", json={"status": "running"})
    assert running.status_code == 200
    assert running.get_json()["status"] == "running"
    assert running.get_json()["result"] is None
    assert running.get_json()["error"] is None

    done = client.patch(f"/tasks/{task_id}", json={"status": "done", "result": {"took_seconds": 2.3}})
    assert done.status_code == 200
    body = done.get_json()
    assert body["status"] == "done"
    assert body["result"] == {"took_seconds": 2.3}
    assert body["error"] is None


def test_update_task_failed_requires_error():
    client = app.test_client()
    created = client.post("/tasks", json={"name": "deploy"})
    task_id = created.get_json()["id"]

    resp = client.patch(f"/tasks/{task_id}", json={"status": "failed"})
    assert resp.status_code == 400


def test_update_task_rejects_invalid_status():
    client = app.test_client()
    created = client.post("/tasks", json={"name": "lint"})
    task_id = created.get_json()["id"]

    resp = client.patch(f"/tasks/{task_id}", json={"status": "weird"})
    assert resp.status_code == 400


def test_delete_task_removes_it():
    client = app.test_client()
    created = client.post("/tasks", json={"name": "clean"})
    task_id = created.get_json()["id"]

    deleted = client.delete(f"/tasks/{task_id}")
    assert deleted.status_code == 204

    # Verify gone
    get_again = client.get(f"/tasks/{task_id}")
    assert get_again.status_code == 404


def test_filter_tasks_by_status():
    client = app.test_client()
    t1 = client.post("/tasks", json={"name": "a"}).get_json()["id"]
    t2 = client.post("/tasks", json={"name": "b"}).get_json()["id"]

    client.patch(f"/tasks/{t1}", json={"status": "running"})

    resp = client.get("/tasks?status=running")
    assert resp.status_code == 200
    tasks = resp.get_json()
    assert len(tasks) == 1
    assert tasks[0]["id"] == t1

    resp2 = client.get("/tasks?status=pending")
    assert resp2.status_code == 200
    tasks2 = resp2.get_json()
    assert len(tasks2) == 1
    assert tasks2[0]["id"] == t2
