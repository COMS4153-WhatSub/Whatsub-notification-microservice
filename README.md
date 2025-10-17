# Notification Microservice (FastAPI)

Placeholder microservice for subscription notifications. API is defined first via `notification-service-openapi.yaml`. The app loads this YAML so Swagger UI reflects the spec. Handlers are placeholders returning 501 for now.

## Tech
- FastAPI
- Uvicorn
- PyYAML (load OpenAPI YAML)

## Structure
```
app/
  main.py                 # App entry; loads YAML, routers, middleware
  resources/
    notifications.py      # Routers/controllers (501 placeholders)
  middleware/
    request_logging.py    # Simple request logging middleware
  models/                 # Pydantic schemas (placeholder)
  services/               # Business logic/persistence adapters (placeholder)
  utils/                  # Utilities (placeholder)
notification-service-openapi.yaml  # API-first spec used by Swagger UI
```

## Setup
```bash
python -m venv .venv && source .venv/bin/activate   # optional
pip install fastapi uvicorn pyyaml
```

## Run
```bash
uvicorn app.main:app --reload
```
- Swagger UI: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`
- OpenAPI YAML: `http://127.0.0.1:8000/openapi.yaml`

Use another port if needed:
```bash
uvicorn app.main:app --reload --port 8080
```

## Quick test (curl)
```bash
# Health
curl -i http://127.0.0.1:8000/health

# List notifications -> 501
curl -i http://127.0.0.1:8000/notifications

# Create notification -> 501
curl -i -X POST http://127.0.0.1:8000/notifications \
  -H 'Content-Type: application/json' \
  -d '{"channel":"email","to":"a@b.com"}'
```

## Notes
- Follow API-first: edit `notification-service-openapi.yaml` first, then implement under `app/resources/` and `app/services/`.
- Middleware, models, services, and utils are scaffolded for future development.
