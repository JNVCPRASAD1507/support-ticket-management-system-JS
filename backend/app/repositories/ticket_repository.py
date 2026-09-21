from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timezone

from app.models.ticket import Ticket


class TicketRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, ticket_id: int) -> Ticket | None:
        statement = (
            select(Ticket)
            .options(
                joinedload(Ticket.category),
                joinedload(Ticket.created_by),
                joinedload(Ticket.assigned_to),
            )
            .where(Ticket.id == ticket_id)
        )

        return self.db.scalar(statement)

    def get_by_ticket_number(
        self,
        ticket_number: str,
    ) -> Ticket | None:
        statement = select(Ticket).where(Ticket.ticket_number == ticket_number)

        return self.db.scalar(statement)

    def get_sla_breached_tickets(self) -> list[Ticket]:
        current_time = datetime.now(timezone.utc)

        statement = (
            select(Ticket)
            .options(
                joinedload(Ticket.category),
                joinedload(Ticket.created_by),
                joinedload(Ticket.assigned_to),
            )
            .where(
                Ticket.sla_due_at.is_not(None),
                Ticket.sla_due_at < current_time,
                Ticket.status.not_in(["resolved", "closed"]),
            )
            .order_by(Ticket.sla_due_at.asc())
        )

        return list(self.db.scalars(statement).unique().all())

    def create(self, ticket: Ticket) -> Ticket:
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)

        return ticket

    def update(self, ticket: Ticket) -> Ticket:
        self.db.commit()
        self.db.refresh(ticket)

        return ticket

    def delete(self, ticket: Ticket) -> None:
        self.db.delete(ticket)
        self.db.commit()

    def get_all(
        self,
        page: int,
        page_size: int,
        search: str | None = None,
        status_filter: str | None = None,
        priority: str | None = None,
        category_id: int | None = None,
    ) -> tuple[list[Ticket], int]:

        conditions = []

        if search:
            search_pattern = f"%{search}%"

            conditions.append(
                or_(
                    Ticket.title.ilike(search_pattern),
                    Ticket.description.ilike(search_pattern),
                    Ticket.ticket_number.ilike(search_pattern),
                )
            )

        if status_filter:
            conditions.append(Ticket.status == status_filter)

        if priority:
            conditions.append(Ticket.priority == priority)

        if category_id is not None:
            conditions.append(Ticket.category_id == category_id)

        count_statement = select(func.count(Ticket.id))

        if conditions:
            count_statement = count_statement.where(*conditions)

        total = self.db.scalar(count_statement) or 0

        offset = (page - 1) * page_size

        statement = (
            select(Ticket)
            .options(
                joinedload(Ticket.category),
                joinedload(Ticket.created_by),
                joinedload(Ticket.assigned_to),
            )
            .order_by(Ticket.id.desc())
            .offset(offset)
            .limit(page_size)
        )

        if conditions:
            statement = statement.where(*conditions)

        tickets = list(self.db.scalars(statement).unique().all())

        return tickets, total
