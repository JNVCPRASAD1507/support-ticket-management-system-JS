
import pytest

from fastapi import HTTPException

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


def test_assign_ticket_to_support_agent():
    agent = FakeUser(
        user_id=5,
        role_name="support_agent",
    )

    db = FakeDB(user=agent)

    service = AssignmentService(db)

    service.repository = FakeRepository()

    result = service.assign_ticket(
        ticket_id=1,
        assigned_to_id=5,
    )

    assert result.assigned_to_id == 5


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
    agent = FakeUser(
        user_id=1,
        role_name="support_agent",
        is_active=False,
    )

    db = FakeDB(user=agent)

    service = AssignmentService(db)

    service.repository = FakeRepository()

    with pytest.raises(HTTPException) as exc_info:
        service.assign_ticket(
            ticket_id=1,
            assigned_to_id=5,
        )

    assert exc_info.value.status_code == 404
    
    