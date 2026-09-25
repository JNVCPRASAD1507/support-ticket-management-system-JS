from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.dependencies.authorization import (
    get_admin,
    get_authenticated_user,
)
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.ticket import (
    TicketCreate,
    TicketListResponse,
    TicketResponse,
    TicketUpdate,
    TicketAssignmentRequest,
    TicketStatusUpdate,
)
from app.services.assignment_service import AssignmentService
from app.services.ticket_workflow_service import TicketWorkflowService
from app.services.ticket_service import TicketService
from app.services.sla_service import SLAService

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
)


@router.post(
    "",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(
    data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    service = TicketService(db)

    return service.create_ticket(
        data=data,
        current_user_id=current_user.id,
    )


@router.get(
    "",
    response_model=TicketListResponse,
)
def get_tickets(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    search: str | None = Query(
        default=None,
        max_length=100,
    ),
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    priority: str | None = Query(
        default=None,
    ),
    category_id: int | None = Query(
        default=None,
        ge=1,
    ),
    db: Session = Depends(get_db),
    _: User = Depends(get_authenticated_user),
):
    service = TicketService(db)

    tickets, total = service.get_tickets(
        page=page,
        page_size=page_size,
        search=search,
        status_filter=status_filter,
        priority=priority,
        category_id=category_id,
    )

    return TicketListResponse(
        items=tickets,
        total=total,
        page=page,
        page_size=page_size,
    )

@router.get(
    "/sla/breached",
    response_model=list[TicketResponse],
)
def get_sla_breached_tickets(
    db: Session = Depends(get_db),
    _: User = Depends(get_authenticated_user),
):
    return SLAService.get_breached_tickets(db)


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_authenticated_user),
):
    service = TicketService(db)

    return service.get_ticket(ticket_id)


@router.put(
    "/{ticket_id}",
    response_model=TicketResponse,
)
def update_ticket(
    ticket_id: int,
    data: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    service = TicketService(db)

    return service.update_ticket(
        ticket_id=ticket_id,
        data=data,
        current_user_id=current_user.id,
        current_user_role=current_user.role.name,
    )


@router.patch(
    "/{ticket_id}/assign",
    response_model=TicketResponse,
)
def assign_ticket(
    ticket_id: int,
    data: TicketAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin),
):
    service = AssignmentService(db)

    return service.assign_ticket(
        ticket_id=ticket_id,
        assigned_to_id=data.assigned_to_id,
        current_user_id=current_user.id,
    )


@router.patch(
    "/{ticket_id}/status",
    response_model=TicketResponse,
)
def change_ticket_status(
    ticket_id: int,
    data: TicketStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    service = TicketWorkflowService(db)

    return service.change_status(
    ticket_id=ticket_id,
    new_status=data.status,
    current_user=current_user,
    )


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin),
):
    service = TicketService(db)

    service.delete_ticket(ticket_id)

    return None
