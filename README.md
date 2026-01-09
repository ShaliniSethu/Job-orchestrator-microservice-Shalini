# Job Orchestrator Microservice (Docker + GitHub Actions + GHCR)

## Endpoints
- `GET /` returns a hello message
- `GET /health` returns `{ "status": "ok" }`
- `GET /tasks` returns a list of Jobs
- `GET /tasks/id` returns the details of that Job

## Run locally
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pytest -q
python app.py
