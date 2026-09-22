
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.authorization import get_authenticated_user
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.comment import (
    CommentCreate,
    CommentResponse,
    CommentUpdate,
)
from app.services.comment_service import CommentService


router = APIRouter(
    prefix="/comments",
    tags=["Comments"],
)


@router.post(
    "/tickets/{ticket_id}",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    ticket_id: int,
    data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    service = CommentService(db)

    return service.create_comment(
        ticket_id=ticket_id,
        data=data,
        current_user_id=current_user.id,
    )


@router.get(
    "/tickets/{ticket_id}",
    response_model=list[CommentResponse],
)
def get_ticket_comments(
    ticket_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_authenticated_user),
):
    service = CommentService(db)

    return service.get_ticket_comments(ticket_id)


@router.put(
    "/{comment_id}",
    response_model=CommentResponse,
)
def update_comment(
    comment_id: int,
    data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    service = CommentService(db)

    return service.update_comment(
        comment_id=comment_id,
        data=data,
        current_user_id=current_user.id,
    )


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    service = CommentService(db)

    service.delete_comment(
        comment_id=comment_id,
        current_user_id=current_user.id,
    )

    return None

