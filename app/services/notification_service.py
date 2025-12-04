from sqlalchemy.exc import DatabaseError
from sqlalchemy import desc
from app.models.notification import NotificationRequest, NotificationRead, NotificationStatus, NotificationType
from app.services.orm_models import NotificationORM, NotificationStatus as ORMNotificationStatus, NotificationType as ORMNotificationType
from typing import Callable, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

class NotificationService:
    def __init__(self, session_factory: Callable[[], Session], logger):
        self.session_factory = session_factory
        self.logger = logger

    def create_notification(self, payload: NotificationRequest) -> int:
        """
        Create a push notification and save to database.
        For push notifications, we queue them and they will be delivered via SSE/WebSocket.
        """
        try:
            with self.session_factory() as session:
                # Map Pydantic enum to SQLAlchemy enum
                notification_type = ORMNotificationType(payload.notification_type.value)
                status = ORMNotificationStatus.queued  # Start as queued for push notifications
                
                notification = NotificationORM(
                    subscription_id=payload.subscription_id,
                    user_id=payload.user_id,
                    notification_type=notification_type,
                    subject=payload.subject,
                    message=payload.body,
                    status=status,
                    recipient_email=payload.recipient_email,
                    device_token=payload.device_token
                )
                
                session.add(notification)
                session.commit()
                session.refresh(notification)
                
                self.logger.info(
                    f"Notification created with ID: {notification.notification_id} "
                    f"for user {payload.user_id}, subscription {payload.subscription_id}"
                )
                
                # For push notifications, mark as sent immediately (delivery happens via SSE)
                if payload.notification_type == NotificationType.push:
                    notification.status = ORMNotificationStatus.sent
                    session.commit()
                
                return notification.notification_id
                
        except Exception as e:
            self.logger.error(f"Failed to create notification: {str(e)}")
            raise RuntimeError(f"Failed to create notification: {str(e)}") from e

    def get_user_notifications(
        self, 
        user_id: str, 
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[NotificationRead]:
        """
        Get notifications for a user, optionally filtered to unread only.
        """
        try:
            with self.session_factory() as session:
                query = session.query(NotificationORM).filter(
                    NotificationORM.user_id == user_id
                )
                
                if unread_only:
                    query = query.filter(NotificationORM.read_at.is_(None))
                
                query = query.order_by(desc(NotificationORM.created_at))
                query = query.limit(limit).offset(offset)
                
                notifications = query.all()
                
                return [
                    NotificationRead(
                        id=n.notification_id,
                        subscription_id=n.subscription_id,
                        user_id=n.user_id,
                        notification_type=NotificationType(n.notification_type.value),
                        subject=n.subject,
                        message=n.message,
                        status=NotificationStatus(n.status.value),
                        read_at=n.read_at,
                        delivered_at=n.delivered_at,
                        created_at=n.created_at
                    )
                    for n in notifications
                ]
        except Exception as e:
            self.logger.error(f"Failed to get notifications for user {user_id}: {str(e)}")
            raise RuntimeError(f"Failed to get notifications: {str(e)}") from e

    def mark_notification_read(self, notification_id: int, user_id: str) -> bool:
        """
        Mark a notification as read by the user.
        """
        try:
            with self.session_factory() as session:
                notification = session.query(NotificationORM).filter(
                    NotificationORM.notification_id == notification_id,
                    NotificationORM.user_id == user_id
                ).first()
                
                if not notification:
                    return False
                
                if notification.read_at is None:
                    notification.read_at = datetime.utcnow()
                    session.commit()
                    self.logger.info(f"Notification {notification_id} marked as read")
                    return True
                
                return True  # Already read
                
        except Exception as e:
            self.logger.error(f"Failed to mark notification {notification_id} as read: {str(e)}")
            raise RuntimeError(f"Failed to mark notification as read: {str(e)}") from e

    def mark_notification_delivered(self, notification_id: int) -> bool:
        """
        Mark a notification as delivered (called by Cloud Function or SSE handler).
        """
        try:
            with self.session_factory() as session:
                notification = session.get(NotificationORM, notification_id)
                
                if not notification:
                    return False
                
                if notification.delivered_at is None:
                    notification.delivered_at = datetime.utcnow()
                    notification.status = ORMNotificationStatus.delivered
                    session.commit()
                    self.logger.info(f"Notification {notification_id} marked as delivered")
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to mark notification {notification_id} as delivered: {str(e)}")
            return False

    def get_unread_count(self, user_id: str) -> int:
        """
        Get count of unread notifications for a user.
        """
        try:
            with self.session_factory() as session:
                count = session.query(NotificationORM).filter(
                    NotificationORM.user_id == user_id,
                    NotificationORM.read_at.is_(None)
                ).count()
                return count
        except Exception as e:
            self.logger.error(f"Failed to get unread count for user {user_id}: {str(e)}")
            return 0

