from datetime import datetime, timedelta, timezone

from app.core.constants import SLA_HOURS
from app.repositories.ticket_repository import TicketRepository


class SLAService:

    @staticmethod
    def calculate_due_at(
        priority: str,
        created_at: datetime | None = None,
    ) -> datetime:

        priority = priority.lower()

        hours = SLA_HOURS.get(priority)

        if hours is None:
            raise ValueError(
                f"Invalid priority: {priority}"
            )

        if created_at is None:
            created_at = datetime.now(timezone.utc)

        return created_at + timedelta(hours=hours)

    @staticmethod
    def is_breached(
        sla_due_at: datetime | None,
        current_time: datetime | None = None,
    ) -> bool:

        if sla_due_at is None:
            return False

        if current_time is None:
            current_time = datetime.now(timezone.utc)

        return current_time > sla_due_at

    @staticmethod
    def get_breached_tickets(db):
        repository = TicketRepository(db)

        return repository.get_sla_breached_tickets()
    
    