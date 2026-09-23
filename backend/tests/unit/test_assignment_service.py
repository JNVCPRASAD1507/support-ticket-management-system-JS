# tests/unit/test_assignment_service.py

import pytest
from fastapi import HTTPException
from unittest.mock import patch

from app.services.assignment_service import AssignmentService


class FakeRole:
    def __init__(self, name):
        self.name = name


class FakeUser:
    def __init__(self, user_id, role_name, is_active=True):
        self.id = user_id
        self.role = FakeRole(role_name)
        self.is_active = is_active


class FakeTicket:
    def __init__(self):
        self.id = 1
        self.ticket_number = "TKT-000001"
        self.assigned_to_id = None


class FakeRepository:
    def __init__(self):
        self.ticket = FakeTicket()

    def get_by_id(self, ticket_id):
        return self.ticket

    def update(self, ticket):
        return ticket


class FakeDB:
    def __init__(self, user=None):
        self.user = user

    def scalar(self, statement):
        return self.user

    def add(self, obj):
        return obj

    def flush(self):
        pass

    def commit(self):
        pass

    def refresh(self, obj):
        return obj


def test_assign_ticket_to_support_agent():
    agent = FakeUser(
        user_id=5,
        role_name="support_agent",
        is_active=True,
    )

    db = FakeDB(user=agent)

    service = AssignmentService(db)
    service.repository = FakeRepository()

    with patch(
        "app.services.assignment_service.NotificationService"
    ) as mock_notification_service:

        result = service.assign_ticket(
            ticket_id=1,
            assigned_to_id=5,
        )

    assert result.assigned_to_id == 5

    mock_notification_service.return_value.create_notification.assert_called_once_with(
        user_id=5,
        title="New Ticket Assigned",
        message="Ticket TKT-000001 has been assigned to you.",
        notification_type="ticket_assigned",
    )


def test_unassign_ticket():
    db = FakeDB()

    service = AssignmentService(db)
    service.repository = FakeRepository()

    service.repository.ticket.assigned_to_id = 5

    result = service.assign_ticket(
        ticket_id=1,
        assigned_to_id=None,
    )

    assert result.assigned_to_id is None


def test_cannot_assign_to_customer():
    customer = FakeUser(
        user_id=3,
        role_name="customer",
        is_active=True,
    )

    db = FakeDB(user=customer)

    service = AssignmentService(db)
    service.repository = FakeRepository()

    with pytest.raises(HTTPException) as exc_info:
        service.assign_ticket(
            ticket_id=1,
            assigned_to_id=3,
        )

    assert exc_info.value.status_code == 400


def test_cannot_assign_to_inactive_agent():
    inactive_agent = FakeUser(
        user_id=1,
        role_name="support_agent",
        is_active=False,
    )

    # Important:
    # The production query contains:
    # User.is_active.is_(True)
    #
    # FakeDB.scalar() must simulate that query by returning None
    # when the user is inactive.
    db = FakeDB(user=None)

    service = AssignmentService(db)
    service.repository = FakeRepository()

    with pytest.raises(HTTPException) as exc_info:
        service.assign_ticket(
            ticket_id=1,
            assigned_to_id=1,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found or inactive"
    
    