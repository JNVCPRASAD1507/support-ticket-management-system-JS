
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.models.user import User
from app.repositories.ticket_repository import TicketRepository


class AssignmentService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = TicketRepository(db)

    def assign_ticket(
        self,
        ticket_id: int,
        assigned_to_id: int | None,
    ) -> Ticket:

        # Get ticket
        ticket = self.repository.get_by_id(ticket_id)

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        # Unassign ticket
        if assigned_to_id is None:
            ticket.assigned_to_id = None
            return self.repository.update(ticket)

        # Find user
        user = self.db.scalar(
            select(User).where(
                User.id == assigned_to_id,
                User.is_active.is_(True),
            )
        )

        # User does not exist
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or inactive",
            )

        # Explicitly validate active state
        # This is also important for mocked/fake repositories used in tests.
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or inactive",
            )

        # Only support agents can be assigned tickets
        if user.role.name != "support_agent":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ticket can only be assigned to a support agent",
            )

        # Assign ticket
        ticket.assigned_to_id = assigned_to_id

        return self.repository.update(ticket)

