from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
import yaml

from .resources.notifications import router as notifications_router
from .middleware.request_logging import RequestLoggingMiddleware

app = FastAPI(title="Subscription Notification Service", version="0.0.1")

app.add_middleware(RequestLoggingMiddleware)

SPEC_PATH = Path(__file__).resolve().parents[1] / "notification-service-openapi.yaml"

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(notifications_router)

@app.get("/openapi.yaml", include_in_schema=False)
def openapi_yaml():
    return FileResponse(str(SPEC_PATH), media_type="text/yaml")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    with SPEC_PATH.open("r", encoding="utf-8") as f:
        schema = yaml.safe_load(f)
    app.openapi_schema = schema
    return app.openapi_schema

app.openapi = custom_openapi

