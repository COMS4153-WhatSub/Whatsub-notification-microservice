from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class NotificationType(str, Enum):
    email = "email"
    sms = "sms"
    push = "push"

class NotificationRequest(BaseModel):
    recipient: EmailStr = Field(..., description="Email address of the recipient")
    subject: str = Field(..., description="Subject line of the notification")
    body: str = Field(..., description="Body content of the notification")
    notification_type: NotificationType = Field(default=NotificationType.email, description="Type of notification")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

class NotificationResponse(BaseModel):
    id: str = Field(..., description="Unique ID of the sent notification")
    status: str = Field(..., description="Status of the notification (sent, queued, failed)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

