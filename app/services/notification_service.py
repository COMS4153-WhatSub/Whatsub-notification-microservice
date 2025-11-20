import uuid
from sqlalchemy.exc import DatabaseError
from app.models.notification import NotificationRequest
from app.services.orm_models import ReminderORM, NotificationStatus
from typing import Callable
from sqlalchemy.orm import Session

class NotificationService:
    def __init__(self, session_factory: Callable[[], Session], logger):
        self.session_factory = session_factory
        self.logger = logger

    def send_notification(self, payload: NotificationRequest) -> str:
        """
        Send notification and log to database.
        """
        notification_id = str(uuid.uuid4())
        
        # 1. Mock Sending Logic
        self.logger.info(f"Attempting to send {payload.notification_type} to {payload.recipient}")
        self.logger.info(f"Subject: {payload.subject}")
        
        # Simulate Success
        status = NotificationStatus.sent
        
        # 2. Save to Database
        try:
            with self.session_factory() as session:
                # Extract metadata if available
                meta = payload.metadata or {}
                subscription_id = meta.get("subscription_id", 0) # Default to 0 if not provided
                user_id = meta.get("user_id")

                reminder = ReminderORM(
                    subscription_id=int(subscription_id) if subscription_id else 0,
                    user_id=str(user_id) if user_id else None,
                    recipient_email=payload.recipient,
                    subject=payload.subject,
                    message=payload.body,
                    status=status
                )
                session.add(reminder)
                session.commit()
                self.logger.info(f"Notification saved to DB with ID: {reminder.reminder_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to save notification log: {str(e)}")
            # We don't fail the request if logging fails, but we log the error
            
        return notification_id

