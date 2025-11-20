import uuid
import logging
from fastapi import APIRouter, HTTPException, status
from app.models.notification import NotificationRequest, NotificationResponse

# Configure logger
logger = logging.getLogger("notification_service")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

router = APIRouter()

@router.get("/notifications")
def list_notifications():
    raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")

@router.post("/notifications", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(payload: NotificationRequest):
    """
    Send a notification (Email/SMS).
    Currently implements a Mock Sender that logs the message.
    """
    notification_id = str(uuid.uuid4())
    
    # Mock Sending Logic
    logger.info(f"Attempting to send {payload.notification_type} to {payload.recipient}")
    logger.info(f"Subject: {payload.subject}")
    logger.info(f"Body: {payload.body}")
    
    # In a real implementation, we would call SendGrid/Twilio here
    # success = email_client.send(...)
    
    # Log success
    logger.info(f"Notification {notification_id} sent successfully.")
    
    return NotificationResponse(
        id=notification_id,
        status="sent",
    )

@router.put("/notifications")
def replace_notifications():
    raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")

@router.delete("/notifications")
def delete_notifications():
    raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")
