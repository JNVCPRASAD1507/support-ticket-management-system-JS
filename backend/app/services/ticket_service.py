from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import (
    TICKET_PRIORITIES,
    TICKET_STATUSES,
)
from app.core.audit_actions import AuditAction

from app.models.category import Category
from app.models.ticket import Ticket

from app.repositories.ticket_repository import TicketRepository

from app.schemas.ticket import TicketCreate, TicketUpdate

from app.services.audit_log_service import create_audit_log
from app.services.sla_service import SLAService

from app.utils.ticket_number import generate_ticket_number


class TicketService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = TicketRepository(db)

    # ---------------------------------------------------------
    # GET SINGLE TICKET
    # ---------------------------------------------------------
    def get_ticket(
        self,
        ticket_id: int,
    ) -> Ticket:

        ticket = self.repository.get_by_id(
            ticket_id
        )

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        return ticket

    # ---------------------------------------------------------
    # GET TICKETS
    # SEARCH + FILTER + PAGINATION
    # ---------------------------------------------------------
    def get_tickets(
        self,
        page: int,
        page_size: int,
        search: str | None = None,
        status_filter: str | None = None,
        priority: str | None = None,
        category_id: int | None = None,
    ):
        if status_filter:
            status_filter = status_filter.lower()

            if status_filter not in TICKET_STATUSES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid ticket status",
                )

        if priority:
            priority = priority.lower()

            if priority not in TICKET_PRIORITIES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid ticket priority",
                )

        return self.repository.get_all(
            page=page,
            page_size=page_size,
            search=search,
            status_filter=status_filter,
            priority=priority,
            category_id=category_id,
        )

    # ---------------------------------------------------------
    # CREATE TICKET
    # ---------------------------------------------------------
    def create_ticket(
        self,
        data: TicketCreate,
        current_user_id: int,
    ) -> Ticket:

        # -----------------------------------------------------
        # VALIDATE PRIORITY
        # -----------------------------------------------------
        priority = data.priority.lower()

        if priority not in TICKET_PRIORITIES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ticket priority",
            )

        # -----------------------------------------------------
        # VALIDATE CATEGORY
        # -----------------------------------------------------
        category = self.db.scalar(
            select(Category).where(
                Category.id == data.category_id,
                Category.is_active.is_(True),
            )
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found or inactive",
            )

        # -----------------------------------------------------
        # CALCULATE SLA
        # -----------------------------------------------------
        sla_due_at = SLAService.calculate_due_at(
            priority=priority,
        )

        # -----------------------------------------------------
        # CREATE TICKET
        # -----------------------------------------------------
        ticket = Ticket(
            ticket_number=generate_ticket_number(),
            title=data.title.strip(),
            description=data.description.strip(),
            status="open",
            priority=priority,
            category_id=data.category_id,
            created_by_id=current_user_id,
            sla_due_at=sla_due_at,
        )

        # -----------------------------------------------------
        # SAVE TICKET
        # -----------------------------------------------------
        ticket = self.repository.create(
            ticket
        )

        # -----------------------------------------------------
        # AUDIT: TICKET CREATED
        # -----------------------------------------------------
        create_audit_log(
            self.db,
            user_id=current_user_id,
            action=AuditAction.TICKET_CREATED,
            entity_type="Ticket",
            entity_id=ticket.id,
            description=(
                f"Ticket '{ticket.title}' "
                f"({ticket.ticket_number}) was created"
            ),
        )

        self.db.commit()
        self.db.refresh(ticket)

        return ticket

    # ---------------------------------------------------------
    # UPDATE TICKET
    # ---------------------------------------------------------
    def update_ticket(
        self,
        ticket_id: int,
        data: TicketUpdate,
        current_user_id: int,
        current_user_role: str,
    ) -> Ticket:

        ticket = self.get_ticket(
            ticket_id
        )

        # -----------------------------------------------------
        # AUTHORIZATION
        # -----------------------------------------------------
        is_admin = current_user_role == "admin"
        is_agent = current_user_role == "support_agent"
        is_owner = ticket.created_by_id == current_user_id

        if not (is_admin or is_agent or is_owner):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission "
                    "to update this ticket"
                ),
            )

        # -----------------------------------------------------
        # STORE OLD VALUES
        # -----------------------------------------------------
        old_title = ticket.title
        old_description = ticket.description
        old_priority = ticket.priority
        old_category_id = ticket.category_id
        old_status = ticket.status

        # Track general changes
        changes = []

        # -----------------------------------------------------
        # UPDATE TITLE
        # -----------------------------------------------------
        if data.title is not None:

            new_title = data.title.strip()

            if new_title != ticket.title:

                ticket.title = new_title

                changes.append(
                    f"title changed from "
                    f"'{old_title}' to '{new_title}'"
                )

        # -----------------------------------------------------
        # UPDATE DESCRIPTION
        # -----------------------------------------------------
        if data.description is not None:

            new_description = data.description.strip()

            if new_description != ticket.description:

                ticket.description = new_description

                changes.append(
                    "description was updated"
                )

        # -----------------------------------------------------
        # UPDATE STATUS
        # -----------------------------------------------------
        if data.status is not None:

            new_status = data.status.lower()

            # Validate status
            if new_status not in TICKET_STATUSES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid ticket status",
                )

            # Only update and audit when status changes
            if new_status != ticket.status:

                ticket.status = new_status

                # -------------------------------------------------
                # AUDIT: STATUS CHANGED
                # -------------------------------------------------
                create_audit_log(
                    self.db,
                    user_id=current_user_id,
                    action=AuditAction.STATUS_CHANGED,
                    entity_type="Ticket",
                    entity_id=ticket.id,
                    description=(
                        f"Ticket '{ticket.ticket_number}' "
                        f"status changed from "
                        f"'{old_status}' to '{new_status}'"
                    ),
                    old_value=str(old_status),
                    new_value=str(new_status),
                )

                changes.append(
                    f"status changed from "
                    f"'{old_status}' to '{new_status}'"
                )

        # -----------------------------------------------------
        # UPDATE PRIORITY
        # -----------------------------------------------------
        if data.priority is not None:

            priority = data.priority.lower()

            if priority not in TICKET_PRIORITIES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid ticket priority",
                )

            if priority != ticket.priority:

                ticket.priority = priority

                # -------------------------------------------------
                # AUDIT: PRIORITY CHANGED
                # -------------------------------------------------
                create_audit_log(
                    self.db,
                    user_id=current_user_id,
                    action=AuditAction.PRIORITY_CHANGED,
                    entity_type="Ticket",
                    entity_id=ticket.id,
                    description=(
                        f"Ticket priority changed "
                        f"from '{old_priority}' "
                        f"to '{priority}'"
                    ),
                    old_value=str(old_priority),
                    new_value=str(priority),
                )

                changes.append(
                    f"priority changed from "
                    f"'{old_priority}' to '{priority}'"
                )

        # -----------------------------------------------------
        # UPDATE CATEGORY
        # -----------------------------------------------------
        if data.category_id is not None:

            category = self.db.scalar(
                select(Category).where(
                    Category.id == data.category_id,
                    Category.is_active.is_(True),
                )
            )

            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category not found or inactive",
                )

            if data.category_id != ticket.category_id:

                ticket.category_id = data.category_id

                # -------------------------------------------------
                # AUDIT: CATEGORY CHANGED
                # -------------------------------------------------
                create_audit_log(
                    self.db,
                    user_id=current_user_id,
                    action=AuditAction.TICKET_UPDATED,
                    entity_type="Ticket",
                    entity_id=ticket.id,
                    description=(
                        f"Ticket category changed "
                        f"from '{old_category_id}' "
                        f"to '{data.category_id}'"
                    ),
                    old_value=str(old_category_id),
                    new_value=str(data.category_id),
                )

                changes.append(
                    f"category changed from "
                    f"'{old_category_id}' "
                    f"to '{data.category_id}'"
                )

        # -----------------------------------------------------
        # UPDATE DATABASE
        # -----------------------------------------------------
        ticket = self.repository.update(
            ticket
        )

        # -----------------------------------------------------
        # GENERAL UPDATE AUDIT
        # -----------------------------------------------------
        if changes:

            create_audit_log(
                self.db,
                user_id=current_user_id,
                action=AuditAction.TICKET_UPDATED,
                entity_type="Ticket",
                entity_id=ticket.id,
                description=(
                    f"Ticket '{ticket.ticket_number}' "
                    f"updated: "
                    + "; ".join(changes)
                ),
            )

        # -----------------------------------------------------
        # COMMIT
        # -----------------------------------------------------
        self.db.commit()
        self.db.refresh(ticket)

        return ticket

    # ---------------------------------------------------------
    # DELETE TICKET
    # ---------------------------------------------------------
    def delete_ticket(
        self,
        ticket_id: int,
        current_user_id: int | None = None,
    ) -> None:

        ticket = self.get_ticket(
            ticket_id
        )

        # Keep values before deletion
        ticket_number = ticket.ticket_number
        ticket_title = ticket.title
        deleted_ticket_id = ticket.id

        # -----------------------------------------------------
        # DELETE TICKET
        # -----------------------------------------------------
        self.repository.delete(
            ticket
        )

        # -----------------------------------------------------
        # AUDIT: TICKET DELETED
        # -----------------------------------------------------
        if current_user_id is not None:

            create_audit_log(
                self.db,
                user_id=current_user_id,
                action=AuditAction.TICKET_UPDATED,
                entity_type="Ticket",
                entity_id=deleted_ticket_id,
                description=(
                    f"Ticket '{ticket_number}' "
                    f"('{ticket_title}') was deleted"
                ),
            )

        self.db.commit()
        
        
        