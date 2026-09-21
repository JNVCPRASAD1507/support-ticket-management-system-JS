from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import (
    TICKET_PRIORITIES,
    TICKET_STATUSES,
)
from app.models.category import Category
from app.models.ticket import Ticket
from app.repositories.ticket_repository import TicketRepository
from app.schemas.ticket import TicketCreate, TicketUpdate
from app.utils.ticket_number import generate_ticket_number
from app.services.sla_service import SLAService


class TicketService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = TicketRepository(db)

    def get_ticket(self, ticket_id: int) -> Ticket:
        ticket = self.repository.get_by_id(ticket_id)

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        return ticket

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

    def create_ticket(
        self,
        data: TicketCreate,
        current_user_id: int,
    ) -> Ticket:

        priority = data.priority.lower()

        if priority not in TICKET_PRIORITIES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ticket priority",
            )

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

        sla_due_at = SLAService.calculate_due_at(
            priority=priority,
        )

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

        return self.repository.create(ticket)

    def update_ticket(
        self,
        ticket_id: int,
        data: TicketUpdate,
        current_user_id: int,
        current_user_role: str,
    ) -> Ticket:

        ticket = self.get_ticket(ticket_id)

        is_admin = current_user_role == "admin"
        is_agent = current_user_role == "support_agent"
        is_owner = ticket.created_by_id == current_user_id

        if not (is_admin or is_agent or is_owner):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update this ticket",
            )

        if data.title is not None:
            ticket.title = data.title.strip()

        if data.description is not None:
            ticket.description = data.description.strip()

        if data.priority is not None:
            priority = data.priority.lower()

            if priority not in TICKET_PRIORITIES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid ticket priority",
                )

            ticket.priority = priority

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

            ticket.category_id = data.category_id

        return self.repository.update(ticket)

    def delete_ticket(
        self,
        ticket_id: int,
    ) -> None:

        ticket = self.get_ticket(ticket_id)

        self.repository.delete(ticket)
