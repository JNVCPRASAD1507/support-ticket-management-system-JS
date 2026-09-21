
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TicketCreate(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=200,
    )

    description: str = Field(
        min_length=5,
    )

    priority: str = "medium"

    category_id: int


class TicketUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=200,
    )

    description: str | None = Field(
        default=None,
        min_length=5,
    )

    priority: str | None = None

    category_id: int | None = None


class TicketResponse(BaseModel):
    id: int
    ticket_number: str
    title: str
    description: str
    status: str
    priority: str
    category_id: int
    created_by_id: int
    assigned_to_id: int | None
    sla_due_at: datetime | None
    created_at: datetime
    updated_at: datetime
    

    model_config = ConfigDict(
        from_attributes=True,
    )


class TicketListResponse(BaseModel):
    items: list[TicketResponse]
    total: int
    page: int
    page_size: int
    

class TicketAssignmentRequest(BaseModel):
    assigned_to_id: int | None
    
class TicketStatusUpdate(BaseModel):
    status: str
    
    