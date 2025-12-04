from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class NotificationType(str, Enum):
    email = "email"
    sms = "sms"
    push = "push"

class NotificationStatus(str, Enum):
    queued = "queued"
    sent = "sent"
    delivered = "delivered"
    failed = "failed"

class NotificationRequest(BaseModel):
    """Request model for creating a notification."""
    user_id: str = Field(..., description="User ID to send notification to")
    subscription_id: int = Field(..., description="Subscription ID this notification is about")
    subject: str = Field(..., description="Subject/title of the notification")
    body: str = Field(..., description="Body content of the notification")
    notification_type: NotificationType = Field(default=NotificationType.push, description="Type of notification")
    # Optional fields for specific notification types
    recipient_email: Optional[str] = Field(default=None, description="Email address (for email notifications)")
    device_token: Optional[str] = Field(default=None, description="Device token (for push notifications)")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

class NotificationRead(BaseModel):
    """Model for reading notification data."""
    id: int = Field(..., description="Notification ID")
    subscription_id: int = Field(..., description="Subscription ID")
    user_id: str = Field(..., description="User ID")
    notification_type: NotificationType = Field(..., description="Type of notification")
    subject: Optional[str] = Field(None, description="Subject/title")
    message: Optional[str] = Field(None, description="Message body")
    status: NotificationStatus = Field(..., description="Current status")
    read_at: Optional[datetime] = Field(None, description="When notification was read")
    delivered_at: Optional[datetime] = Field(None, description="When notification was delivered")
    created_at: datetime = Field(..., description="When notification was created")

class NotificationResponse(BaseModel):
    """Response model for notification creation."""
    id: int = Field(..., description="Notification ID")
    status: NotificationStatus = Field(..., description="Status of the notification")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

