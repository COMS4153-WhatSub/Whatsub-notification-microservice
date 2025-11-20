import logging
from fastapi import FastAPI
from app.utils.settings import get_settings
from app.utils.db import get_session_factory, create_all, get_engine
from app.services.notification_service import NotificationService
from app.resources.notifications import router as notifications_router
from app.middleware.request_logging import RequestLoggingMiddleware

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("whatsub-notification")

settings = get_settings()

app = FastAPI(title="Subscription Notification Service", version="0.0.1")

app.add_middleware(RequestLoggingMiddleware)

# Database & Service Init
@app.on_event("startup")
def startup_event():
    try:
        engine = get_engine()
        create_all(engine)
        session_factory = get_session_factory()
        app.state.notification_service = NotificationService(session_factory, logger)
        logger.info("Service started and DB connected")
    except Exception as e:
        logger.error(f"Failed to start service: {e}")
        # In production, might want to raise to fail fast, but for now allow startup
        # raise e

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(notifications_router)
