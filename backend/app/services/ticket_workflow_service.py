
from fastapi import HTTPException, status

from app.models.ticket import Ticket
from app.repositories.ticket_repository import TicketRepository


ALLOWED_TRANSITIONS = {
    "open": {
        "in_progress",
    },
    "in_progress": {
        "resolved",
    },
    "resolved": {
        "closed",
        "in_progress",
    },
    "closed": set(),
}


class TicketWorkflowService:

    def __init__(self, db):
        self.repository = TicketRepository(db)

    def change_status(
        self,
        ticket_id: int,
        new_status: str,
    ) -> Ticket:

        ticket = self.repository.get_by_id(ticket_id)

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        new_status = new_status.lower()

        allowed_statuses = ALLOWED_TRANSITIONS.get(
            ticket.status,
            set(),
        )

        if new_status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Cannot change ticket status "
                    f"from '{ticket.status}' to '{new_status}'"
                ),
            )

        ticket.status = new_status

        return self.repository.update(ticket)
    
    