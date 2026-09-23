
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.audit_actions import AuditAction
from app.models.ticket import Ticket
from app.models.user import User
from app.repositories.ticket_repository import TicketRepository
from app.services.audit_log_service import create_audit_log
from app.services.notification_service import NotificationService
from app.core.exceptions import NotFoundException


class AssignmentService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = TicketRepository(db)

    def assign_ticket(
        self,
        ticket_id: int,
        assigned_to_id: int | None,
        current_user_id: int | None = None,
    ) -> Ticket:

        # ---------------------------------------------------------
        # Get ticket
        # ---------------------------------------------------------
        ticket = self.repository.get_by_id(ticket_id)

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        # Store old assignee before changing anything
        old_assignee_id = ticket.assigned_to_id

        # ---------------------------------------------------------
        # UNASSIGN TICKET
        # ---------------------------------------------------------
        if assigned_to_id is None:

            # Nothing to change
            if old_assignee_id is None:
                return ticket

            ticket.assigned_to_id = None

            ticket = self.repository.update(ticket)

            # Audit unassignment
            create_audit_log(
                self.db,
                user_id=current_user_id,
                action=AuditAction.TICKET_UNASSIGNED,
                entity_type="Ticket",
                entity_id=ticket.id,
                description=(
                    f"Ticket {ticket.ticket_number} "
                    f"was unassigned from user {old_assignee_id}"
                ),
                old_value=str(old_assignee_id),
                new_value=None,
            )

            self.db.commit()
            self.db.refresh(ticket)

            return ticket

        # ---------------------------------------------------------
        # FIND ASSIGNED USER
        # ---------------------------------------------------------
        user = self.db.scalar(
            select(User).where(
                User.id == assigned_to_id,
                User.is_active.is_(True),
            )
        )

        # User does not exist or is inactive
        if not user:
            raise NotFoundException(
                # status_code=status.HTTP_404_NOT_FOUND,
                code="USER_NOT_FOUND",
                # detail="User not found or inactive",
                message="User not found or inactive",
            )

        # ---------------------------------------------------------
        # ONLY SUPPORT AGENTS CAN BE ASSIGNED
        # ---------------------------------------------------------
        if user.role.name != "support_agent":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ticket can only be assigned to a support agent",
            )

        # ---------------------------------------------------------
        # ASSIGN TICKET
        # ---------------------------------------------------------
        ticket.assigned_to_id = assigned_to_id

        ticket = self.repository.update(ticket)

        # ---------------------------------------------------------
        # AUDIT ASSIGNMENT
        # ---------------------------------------------------------
        create_audit_log(
            self.db,
            user_id=current_user_id,
            action=AuditAction.TICKET_ASSIGNED,
            entity_type="Ticket",
            entity_id=ticket.id,
            description=(
                f"Ticket {ticket.ticket_number} "
                f"was assigned to user {assigned_to_id}"
            ),
            old_value=(
                str(old_assignee_id)
                if old_assignee_id is not None
                else None
            ),
            new_value=str(assigned_to_id),
        )

        # ---------------------------------------------------------
        # NOTIFICATION
        # ---------------------------------------------------------
        NotificationService(self.db).create_notification(
            user_id=assigned_to_id,
            title="New Ticket Assigned",
            message=(
                f"Ticket {ticket.ticket_number} "
                f"has been assigned to you."
            ),
            notification_type="ticket_assigned",
        )

        self.db.commit()
        self.db.refresh(ticket)

        return ticket


