from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, func
from app.utils.db import Base
import enum
from datetime import datetime

class NotificationStatus(str, enum.Enum):
    sent = "sent"
    failed = "failed"
    queued = "queued"

class ReminderORM(Base):
    __tablename__ = "reminders"

    reminder_id = Column(Integer, primary_key=True, autoincrement=True)
    subscription_id = Column(Integer, nullable=False, index=True)
    user_id = Column(String(36), nullable=True)
    recipient_email = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=True)
    message = Column(Text, nullable=True)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.sent, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())

