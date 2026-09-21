
import pytest

from fastapi import HTTPException

from app.services.ticket_workflow_service import (
    TicketWorkflowService,
)


class FakeTicket:
    def __init__(self, status):
        self.id = 1
        self.status = status


class FakeRepository:
    def __init__(self, ticket):
        self.ticket = ticket

    def get_by_id(self, ticket_id):
        return self.ticket

    def update(self, ticket):
        return ticket


class FakeDB:
    pass


def test_open_to_in_progress():
    ticket = FakeTicket("open")

    service = TicketWorkflowService(FakeDB())

    service.repository = FakeRepository(ticket)

    result = service.change_status(
        ticket_id=1,
        new_status="in_progress",
    )

    assert result.status == "in_progress"


def test_in_progress_to_resolved():
    ticket = FakeTicket("in_progress")

    service = TicketWorkflowService(FakeDB())

    service.repository = FakeRepository(ticket)

    result = service.change_status(
        ticket_id=1,
        new_status="resolved",
    )

    assert result.status == "resolved"


def test_resolved_to_closed():
    ticket = FakeTicket("resolved")

    service = TicketWorkflowService(FakeDB())

    service.repository = FakeRepository(ticket)

    result = service.change_status(
        ticket_id=1,
        new_status="closed",
    )

    assert result.status == "closed"


def test_resolved_can_return_to_in_progress():
    ticket = FakeTicket("resolved")

    service = TicketWorkflowService(FakeDB())

    service.repository = FakeRepository(ticket)

    result = service.change_status(
        ticket_id=1,
        new_status="in_progress",
    )

    assert result.status == "in_progress"


def test_open_cannot_go_directly_to_closed():
    ticket = FakeTicket("open")

    service = TicketWorkflowService(FakeDB())

    service.repository = FakeRepository(ticket)

    with pytest.raises(HTTPException) as exc_info:
        service.change_status(
            ticket_id=1,
            new_status="closed",
        )

    assert exc_info.value.status_code == 400


def test_closed_ticket_cannot_change_status():
    ticket = FakeTicket("closed")

    service = TicketWorkflowService(FakeDB())

    service.repository = FakeRepository(ticket)

    with pytest.raises(HTTPException) as exc_info:
        service.change_status(
            ticket_id=1,
            new_status="open",
        )

    assert exc_info.value.status_code == 400
    
    