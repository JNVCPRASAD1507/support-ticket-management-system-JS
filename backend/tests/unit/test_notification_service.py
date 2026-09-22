
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.services.notification_service import NotificationService


class FakeRepository:
    def __init__(self):
        self.notifications = {}

    def get_by_id(self, notification_id):
        return self.notifications.get(notification_id)

    def get_by_user(self, user_id, unread_only=False):
        notifications = [
            notification
            for notification in self.notifications.values()
            if notification.user_id == user_id
        ]

        if unread_only:
            notifications = [
                notification
                for notification in notifications
                if not notification.is_read
            ]

        return notifications

    def count_unread(self, user_id):
        return sum(
            1
            for notification in self.notifications.values()
            if notification.user_id == user_id
            and not notification.is_read
        )

    def create(self, notification):
        notification.id = len(self.notifications) + 1
        self.notifications[notification.id] = notification
        return notification

    def mark_as_read(self, notification):
        notification.is_read = True
        return notification

    def mark_all_as_read(self, user_id):
        notifications = self.get_by_user(
            user_id=user_id,
            unread_only=True,
        )

        for notification in notifications:
            notification.is_read = True

        return len(notifications)

    def delete(self, notification):
        del self.notifications[notification.id]


@pytest.fixture
def service():
    service = NotificationService.__new__(
        NotificationService
    )

    service.db = None
    service.repository = FakeRepository()

    return service


def test_create_notification(service):
    notification = service.create_notification(
        user_id=1,
        title="Test Notification",
        message="Test message",
        notification_type="ticket_created",
    )

    assert notification.id == 1
    assert notification.user_id == 1
    assert notification.title == "Test Notification"
    assert notification.message == "Test message"
    assert notification.notification_type == "ticket_created"
    assert notification.is_read is False


def test_get_user_notifications(service):
    service.create_notification(
        user_id=1,
        title="Notification 1",
        message="Message 1",
        notification_type="ticket_created",
    )

    service.create_notification(
        user_id=2,
        title="Notification 2",
        message="Message 2",
        notification_type="ticket_assigned",
    )

    notifications = service.get_user_notifications(
        user_id=1
    )

    assert len(notifications) == 1
    assert notifications[0].user_id == 1


def test_get_unread_notifications(service):
    notification = service.create_notification(
        user_id=1,
        title="Notification",
        message="Message",
        notification_type="ticket_created",
    )

    notification.is_read = True

    service.create_notification(
        user_id=1,
        title="Unread",
        message="Unread message",
        notification_type="ticket_assigned",
    )

    notifications = service.get_user_notifications(
        user_id=1,
        unread_only=True,
    )

    assert len(notifications) == 1
    assert notifications[0].title == "Unread"


def test_get_unread_count(service):
    service.create_notification(
        user_id=1,
        title="Notification 1",
        message="Message 1",
        notification_type="ticket_created",
    )

    service.create_notification(
        user_id=1,
        title="Notification 2",
        message="Message 2",
        notification_type="ticket_assigned",
    )

    assert service.get_unread_count(1) == 2


def test_mark_as_read(service):
    notification = service.create_notification(
        user_id=1,
        title="Notification",
        message="Message",
        notification_type="ticket_created",
    )

    result = service.mark_as_read(
        notification_id=notification.id,
        current_user_id=1,
    )

    assert result.is_read is True


def test_cannot_mark_other_users_notification_as_read(service):
    notification = service.create_notification(
        user_id=1,
        title="Notification",
        message="Message",
        notification_type="ticket_created",
    )

    with pytest.raises(HTTPException) as exc_info:
        service.mark_as_read(
            notification_id=notification.id,
            current_user_id=2,
        )

    assert exc_info.value.status_code == 403


def test_mark_all_as_read(service):
    service.create_notification(
        user_id=1,
        title="Notification 1",
        message="Message 1",
        notification_type="ticket_created",
    )

    service.create_notification(
        user_id=1,
        title="Notification 2",
        message="Message 2",
        notification_type="ticket_assigned",
    )

    service.create_notification(
        user_id=2,
        title="Other notification",
        message="Message",
        notification_type="ticket_created",
    )

    count = service.mark_all_as_read(1)

    assert count == 2
    assert service.get_unread_count(1) == 0
    assert service.get_unread_count(2) == 1


def test_cannot_delete_other_users_notification(service):
    notification = service.create_notification(
        user_id=1,
        title="Notification",
        message="Message",
        notification_type="ticket_created",
    )

    with pytest.raises(HTTPException) as exc_info:
        service.delete_notification(
            notification_id=notification.id,
            current_user_id=2,
        )

    assert exc_info.value.status_code == 403


def test_delete_notification(service):
    notification = service.create_notification(
        user_id=1,
        title="Notification",
        message="Message",
        notification_type="ticket_created",
    )

    service.delete_notification(
        notification_id=notification.id,
        current_user_id=1,
    )

    assert (
        service.repository.get_by_id(notification.id)
        is None
    )
    
    