from fastapi import HTTPException, status
from app.models.user import User
from app.models.ticket import Ticket
from app.repositories.ticket_repository import TicketRepository
from app.core.audit_actions import AuditAction
from app.services.audit_log_service import create_audit_log
from app.services.notification_service import NotificationService


ALLOWED_TRANSITIONS = {
    "open": {"open", "in_progress"},
    "in_progress": {"in_progress", "resolved"},
    "resolved": {"resolved", "closed", "in_progress"},
    "closed": {"closed"},
}


class TicketWorkflowService:
    def __init__(self, db):
        self.repository = TicketRepository(db)
        self.db = db

    def change_status(self, ticket_id: int, new_status: str, current_user: User) -> Ticket:
        ticket = self.repository.get_by_id(ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

        role = current_user.role.name.lower()
        is_admin = role == "admin"
        is_agent = role == "support_agent"
        is_customer = role == "customer"

        if not (is_admin or is_agent or is_customer):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to change ticket status")

        if is_customer and ticket.created_by_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Customers can only change their own tickets")

        if is_agent and ticket.assigned_to_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Agents can only change tickets assigned to them")

        new_status = new_status.lower().strip()
        if new_status not in ALLOWED_TRANSITIONS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ticket status")

        allowed_statuses = ALLOWED_TRANSITIONS.get(ticket.status, set())
        if new_status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot change ticket status from '{ticket.status}' to '{new_status}'",
            )

        if ticket.status == new_status:
            return ticket

        old_status = ticket.status
        ticket.status = new_status
        ticket = self.repository.update(ticket)

        create_audit_log(
            self.db,
            user_id=current_user.id,
            action=AuditAction.STATUS_CHANGED,
            entity_type="Ticket",
            entity_id=ticket.id,
            description=f"Ticket '{ticket.ticket_number}' status changed from '{old_status}' to '{new_status}'",
            old_value=old_status,
            new_value=new_status,
        )

        recipients = {ticket.created_by_id}
        if ticket.assigned_to_id is not None:
            recipients.add(ticket.assigned_to_id)
        recipients.discard(current_user.id)
        notification_service = NotificationService(self.db)
        for user_id in recipients:
            notification_service.create_notification(
                user_id=user_id,
                title="Ticket Status Updated",
                message=f"Ticket {ticket.ticket_number} status changed from {old_status} to {new_status}.",
                notification_type="ticket_status_changed",
            )

        self.db.commit()
        self.db.refresh(ticket)
        return ticket
