from fastapi import APIRouter, HTTPException, status, Request, Query, Path
from fastapi.responses import StreamingResponse
from app.models.notification import (
    NotificationRequest, 
    NotificationResponse, 
    NotificationRead,
    NotificationStatus
)
from typing import List
import json
import asyncio
from datetime import datetime

router = APIRouter()

def get_notification_service(request: Request):
    """Helper to get notification service from app state."""
    if not hasattr(request.app.state, "notification_service"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Notification Service not initialized"
        )
    return request.app.state.notification_service

@router.post("/notifications", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(payload: NotificationRequest, request: Request):
    """
    Create a push notification and save to database.
    This endpoint is called by the Cloud Function when processing Pub/Sub events.
    """
    service = get_notification_service(request)
    
    try:
        notification_id = service.create_notification(payload)
        
        return NotificationResponse(
            id=notification_id,
            status=NotificationStatus.sent,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create notification: {str(e)}"
        )

@router.get("/notifications", response_model=List[NotificationRead])
def get_notifications(
    user_id: str = Query(..., description="User ID to get notifications for"),
    unread_only: bool = Query(False, description="Filter to unread notifications only"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of notifications to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    request: Request = None
):
    """
    Get notifications for a user.
    """
    service = get_notification_service(request)
    
    try:
        notifications = service.get_user_notifications(
            user_id=user_id,
            unread_only=unread_only,
            limit=limit,
            offset=offset
        )
        return notifications
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notifications: {str(e)}"
        )

@router.get("/notifications/unread-count")
def get_unread_count(
    user_id: str = Query(..., description="User ID to get unread count for"),
    request: Request = None
):
    """
    Get count of unread notifications for a user.
    """
    service = get_notification_service(request)
    
    try:
        count = service.get_unread_count(user_id)
        return {"user_id": user_id, "unread_count": count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get unread count: {str(e)}"
        )

@router.patch("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    user_id: str = Query(..., description="User ID (for security validation)"),
    request: Request = None
):
    """
    Mark a notification as read.
    """
    service = get_notification_service(request)
    
    try:
        success = service.mark_notification_read(notification_id, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found or does not belong to user"
            )
        return {"message": "Notification marked as read", "notification_id": notification_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notification as read: {str(e)}"
        )

@router.delete("/notifications/subscription/{subscription_id}")
def delete_notifications_by_subscription(
    subscription_id: int = Path(..., description="Subscription ID to delete notifications for"),
    request: Request = None
):
    """
    Delete all notifications associated with a subscription.
    This endpoint is called when a subscription is deleted to maintain data consistency.
    """
    service = get_notification_service(request)
    
    try:
        deleted_count = service.delete_notifications_by_subscription_id(subscription_id)
        return {
            "message": f"Deleted {deleted_count} notifications for subscription {subscription_id}",
            "subscription_id": subscription_id,
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete notifications for subscription {subscription_id}: {str(e)}"
        )

@router.get("/notifications/stream")
async def stream_notifications(
    user_id: str = Query(..., description="User ID to stream notifications for"),
    request: Request = None
):
    """
    Server-Sent Events (SSE) endpoint for real-time notification delivery.
    Frontend connects to this endpoint to receive push notifications.
    """
    service = get_notification_service(request)
    
    async def event_generator():
        """Generate SSE events for new notifications."""
        last_check = datetime.utcnow()
        
        while True:
            try:
                # Check for new notifications since last check
                # We'll check for notifications created after last_check
                # For simplicity, we'll check unread notifications
                notifications = service.get_user_notifications(
                    user_id=user_id,
                    unread_only=True,
                    limit=10
                )
                
                # Filter to only notifications created after last_check
                new_notifications = [
                    n for n in notifications 
                    if n.created_at > last_check
                ]
                
                for notification in new_notifications:
                    # Mark as delivered
                    service.mark_notification_delivered(notification.id)
                    
                    # Send SSE event
                    event_data = {
                        "id": notification.id,
                        "subscription_id": notification.subscription_id,
                        "subject": notification.subject,
                        "message": notification.message,
                        "created_at": notification.created_at.isoformat()
                    }
                    yield f"data: {json.dumps(event_data)}\n\n"
                
                # Update last check time
                last_check = datetime.utcnow()
                
                # Keep connection alive with heartbeat
                yield ": heartbeat\n\n"
                
                # Wait before next check (polling interval)
                await asyncio.sleep(2)  # Check every 2 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                error_data = {"error": str(e)}
                yield f"data: {json.dumps(error_data)}\n\n"
                await asyncio.sleep(5)  # Wait longer on error
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable buffering for nginx
        }
    )
