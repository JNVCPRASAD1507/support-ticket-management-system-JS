from fastapi import HTTPException, status

from app.models.user import User
from app.models.ticket import Ticket
from app.repositories.ticket_repository import TicketRepository


ALLOWED_TRANSITIONS = {
    "open": {
        "open",
        "in_progress",
    },
    "in_progress": {
        "in_progress",
        "resolved",
    },
    "resolved": {
        "resolved",
        "closed",
        "in_progress",
    },
    "closed": {
        "closed",
    },
}


class TicketWorkflowService:

    def __init__(self, db):
        self.repository = TicketRepository(db)
        self.db = db

    def change_status(
        self,
        ticket_id: int,
        new_status: str,
        current_user: User,
    ) -> Ticket:

        ticket = self.repository.get_by_id(ticket_id)

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        user_role = current_user.role.name.lower()

        allowed_roles = {
            "admin",
            "support_agent",
            "customer",
        }

        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to change ticket status",
            )

        new_status = new_status.lower().strip()

        allowed_statuses = ALLOWED_TRANSITIONS.get(
            ticket.status,
            set(),
        )

        if new_status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Cannot change ticket status "
                    f"from '{ticket.status}' "
                    f"to '{new_status}'"
                ),
            )

        # Nothing changed
        if ticket.status == new_status:
            return ticket

        ticket.status = new_status

        ticket = self.repository.update(ticket)

        self.db.commit()
        self.db.refresh(ticket)

        return ticket
    
    