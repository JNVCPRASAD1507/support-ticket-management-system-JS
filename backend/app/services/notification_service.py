
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository


class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = NotificationRepository(db)

    def create_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        notification_type: str,
    ) -> Notification:

        notification = Notification(
            user_id=user_id,
            title=title.strip(),
            message=message.strip(),
            notification_type=notification_type.strip().lower(),
            is_read=False,
        )

        return self.repository.create(notification)

    def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
    ) -> list[Notification]:

        return self.repository.get_by_user(
            user_id=user_id,
            unread_only=unread_only,
        )

    def get_unread_count(
        self,
        user_id: int,
    ) -> int:

        return self.repository.count_unread(user_id)

    def mark_as_read(
        self,
        notification_id: int,
        current_user_id: int,
    ) -> Notification:

        notification = self.repository.get_by_id(
            notification_id
        )

        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found",
            )

        if notification.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own notifications",
            )

        return self.repository.mark_as_read(notification)

    def mark_all_as_read(
        self,
        current_user_id: int,
    ) -> int:

        return self.repository.mark_all_as_read(
            current_user_id
        )

    def delete_notification(
        self,
        notification_id: int,
        current_user_id: int,
    ) -> None:

        notification = self.repository.get_by_id(
            notification_id
        )

        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found",
            )

        if notification.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own notifications",
            )

        self.repository.delete(notification)
        
        
        
        