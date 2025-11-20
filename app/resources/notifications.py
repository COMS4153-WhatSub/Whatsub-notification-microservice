from fastapi import APIRouter, HTTPException, status, Request
from app.models.notification import NotificationRequest, NotificationResponse

router = APIRouter()

@router.post("/notifications", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(payload: NotificationRequest, request: Request):
    """
    Send a notification (Email/SMS) and log to database.
    """
    # Access service from app state
    if not hasattr(request.app.state, "notification_service"):
        raise HTTPException(status_code=500, detail="Notification Service not initialized")
        
    service = request.app.state.notification_service
    
    notification_id = service.send_notification(payload)
    
    return NotificationResponse(
        id=notification_id,
        status="sent",
    )
