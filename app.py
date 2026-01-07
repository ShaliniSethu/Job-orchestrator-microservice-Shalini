from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
from typing import Any, Dict, Optional

from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory store (simple + perfect for this project)
# Format: { "<task_id>": {task_dict} }
TASKS: Dict[str, Dict[str, Any]] = {}

ALLOWED_STATUSES = {"pending", "running", "done", "failed"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_error(message: str, status_code: int = 400):
    return jsonify({"error": message}), status_code


@app.get("/")
def home():
    return jsonify(message="Hello from Flask CI/CD demo!")


@app.get("/health")
def health():
    return jsonify(status="ok"), 200


@app.post("/tasks")
def create_task():
    if not request.is_json:
        return make_error("Request body must be JSON", 400)

    data = request.get_json(silent=True) or {}
    name = data.get("name")
    payload = data.get("payload")

    if not isinstance(name, str) or not name.strip():
        return make_error("Field 'name' is required and must be a non-empty string", 400)

    task_id = str(uuid4())
    now = utc_now_iso()

    task = {
        "id": task_id,
        "name": name.strip(),
        "status": "pending",
        "payload": payload,         # can be any JSON value
        "result": None,             # filled when done
        "error": None,              # filled when failed
        "created_at": now,
        "updated_at": now,
    }

    TASKS[task_id] = task
    return jsonify(task), 201


@app.get("/tasks")
def list_tasks():
    status = request.args.get("status")
    tasks = list(TASKS.values())

    if status is not None:
        if status not in ALLOWED_STATUSES:
            return make_error(f"Invalid status filter. Allowed: {sorted(ALLOWED_STATUSES)}", 400)
        tasks = [t for t in tasks if t["status"] == status]

    # Sort newest first (nice UX)
    tasks.sort(key=lambda t: t["created_at"], reverse=True)
    return jsonify(tasks), 200


@app.get("/tasks/<task_id>")
def get_task(task_id: str):
    task = TASKS.get(task_id)
    if task is None:
        return make_error("Task not found", 404)
    return jsonify(task), 200


@app.patch("/tasks/<task_id>")
def update_task(task_id: str):
    task = TASKS.get(task_id)
    if task is None:
        return make_error("Task not found", 404)

    if not request.is_json:
        return make_error("Request body must be JSON", 400)

    data = request.get_json(silent=True) or {}

    # Only allow updating specific fields
    status = data.get("status")
    result = data.get("result")
    error = data.get("error")

    if status is None:
        return make_error("Field 'status' is required", 400)

    if status not in ALLOWED_STATUSES:
        return make_error(f"Invalid status. Allowed: {sorted(ALLOWED_STATUSES)}", 400)

    # Basic rules (keeps it realistic)
    if status == "failed" and (not isinstance(error, str) or not error.strip()):
        return make_error("Field 'error' is required when status is 'failed'", 400)

    if status == "done":
        # result can be anything JSON, optional
        task["result"] = result
        task["error"] = None
    elif status == "failed":
        task["error"] = error.strip()
        task["result"] = None
    else:
        # pending/running: clear result/error by default (simple state model)
        task["result"] = None
        task["error"] = None

    task["status"] = status
    task["updated_at"] = utc_now_iso()

    return jsonify(task), 200


@app.delete("/tasks/<task_id>")
def delete_task(task_id: str):
    if task_id not in TASKS:
        return make_error("Task not found", 404)

    del TASKS[task_id]
    return ("", 204)


# Handy for tests and local dev
def clear_tasks() -> None:
    TASKS.clear()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

