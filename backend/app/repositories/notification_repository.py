
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        notification_id: int,
    ) -> Notification | None:
        statement = select(Notification).where(
            Notification.id == notification_id
        )

        return self.db.scalar(statement)

    def get_by_user(
        self,
        user_id: int,
        unread_only: bool = False,
    ) -> list[Notification]:
        statement = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.id.desc())
        )

        if unread_only:
            statement = statement.where(
                Notification.is_read.is_(False)
            )

        return list(self.db.scalars(statement).all())

    def count_unread(
        self,
        user_id: int,
    ) -> int:
        statement = select(
            func.count(Notification.id)
        ).where(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )

        return self.db.scalar(statement) or 0

    def create(
        self,
        notification: Notification,
    ) -> Notification:
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)

        return notification

    def mark_as_read(
        self,
        notification: Notification,
    ) -> Notification:
        notification.is_read = True

        self.db.commit()
        self.db.refresh(notification)

        return notification

    def mark_all_as_read(
        self,
        user_id: int,
    ) -> int:
        notifications = self.get_by_user(
            user_id=user_id,
            unread_only=True,
        )

        for notification in notifications:
            notification.is_read = True

        self.db.commit()

        return len(notifications)

    def delete(
        self,
        notification: Notification,
    ) -> None:
        self.db.delete(notification)
        self.db.commit()
        
        
        