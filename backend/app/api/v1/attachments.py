
from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.dependencies.authorization import (
    get_authenticated_user,
)
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.attachment import AttachmentResponse
from app.services.attachment_service import (
    AttachmentService,
)


router = APIRouter(
    prefix="/attachments",
    tags=["Attachments"],
)


@router.post(
    "/tickets/{ticket_id}",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_attachment(
    ticket_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_authenticated_user
    ),
):
    service = AttachmentService(db)

    return await service.upload_attachment(
        ticket_id=ticket_id,
        file=file,
        current_user_id=current_user.id,
    )


@router.get(
    "/tickets/{ticket_id}",
    response_model=list[AttachmentResponse],
)
def get_ticket_attachments(
    ticket_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(
        get_authenticated_user
    ),
):
    service = AttachmentService(db)

    return service.get_ticket_attachments(
        ticket_id
    )


@router.delete(
    "/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_authenticated_user
    ),
):
    service = AttachmentService(db)

    service.delete_attachment(
        attachment_id=attachment_id,
        current_user_id=current_user.id,
    )

    return None

