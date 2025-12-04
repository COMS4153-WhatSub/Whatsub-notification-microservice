from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, func
from app.utils.db import Base
import enum
from datetime import datetime
from typing import Optional

class NotificationStatus(str, enum.Enum):
    queued = "queued"
    sent = "sent"
    delivered = "delivered"
    failed = "failed"

class NotificationType(str, enum.Enum):
    email = "email"
    sms = "sms"
    push = "push"

class NotificationORM(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, autoincrement=True)
    subscription_id = Column(Integer, nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    notification_type = Column(Enum(NotificationType), default=NotificationType.push, nullable=False)
    subject = Column(String(255), nullable=True)
    message = Column(Text, nullable=True)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.queued, index=True)
    # Optional fields for different notification types
    recipient_email = Column(String(255), nullable=True)  # For email notifications
    device_token = Column(String(500), nullable=True)  # For push notifications (FCM)
    # Tracking fields
    read_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, server_default=func.now())

