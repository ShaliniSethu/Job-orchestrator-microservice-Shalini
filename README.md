# Flask CI/CD Demo (Docker + GitHub Actions + GHCR)

## Endpoints
- `GET /` returns a hello message
- `GET /health` returns `{ "status": "ok" }`

## Run locally
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pytest -q
python app.py
