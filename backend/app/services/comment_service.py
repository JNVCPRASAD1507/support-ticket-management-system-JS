
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.ticket import Ticket
from app.repositories.comment_repository import CommentRepository
from app.schemas.comment import CommentCreate, CommentUpdate


class CommentService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = CommentRepository(db)

    def get_comment(self, comment_id: int) -> Comment:
        comment = self.repository.get_by_id(comment_id)

        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found",
            )

        return comment

    def get_ticket_comments(self, ticket_id: int) -> list[Comment]:
        ticket = self.db.get(Ticket, ticket_id)

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        return self.repository.get_by_ticket(ticket_id)

    def create_comment(
        self,
        ticket_id: int,
        data: CommentCreate,
        current_user_id: int,
    ) -> Comment:

        ticket = self.db.get(Ticket, ticket_id)

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        comment = Comment(
            ticket_id=ticket_id,
            user_id=current_user_id,
            content=data.content.strip(),
        )

        return self.repository.create(comment)

    def update_comment(
        self,
        comment_id: int,
        data: CommentUpdate,
        current_user_id: int,
    ) -> Comment:

        comment = self.get_comment(comment_id)

        if comment.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own comments",
            )

        comment.content = data.content.strip()

        return self.repository.update(comment)

    def delete_comment(
        self,
        comment_id: int,
        current_user_id: int,
    ) -> None:

        comment = self.get_comment(comment_id)

        if comment.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own comments",
            )

        self.repository.delete(comment)
        
        