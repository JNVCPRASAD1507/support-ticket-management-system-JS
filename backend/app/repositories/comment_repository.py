from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.comment import Comment


class CommentRepository:

    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------------
    # GET SINGLE COMMENT
    # ---------------------------------------------------------
    def get_by_id(
        self,
        comment_id: int,
    ) -> Comment | None:

        statement = (
            select(Comment)
            .options(joinedload(Comment.user))
            .where(Comment.id == comment_id)
        )

        return self.db.scalar(statement)

    # ---------------------------------------------------------
    # GET COMMENTS FOR TICKET
    # ---------------------------------------------------------
    def get_by_ticket(
        self,
        ticket_id: int,
    ) -> list[Comment]:

        statement = (
            select(Comment)
            .options(joinedload(Comment.user))
            .where(Comment.ticket_id == ticket_id)
            .order_by(Comment.id.asc())
        )

        return list(self.db.scalars(statement).unique().all())

    # ---------------------------------------------------------
    # CREATE
    # ---------------------------------------------------------
    def create(
        self,
        comment: Comment,
    ) -> Comment:

        self.db.add(comment)

        self.db.flush()

        return comment

    # ---------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------
    def update(
        self,
        comment: Comment,
    ) -> Comment:

        self.db.flush()

        return comment

    # ---------------------------------------------------------
    # DELETE
    # ---------------------------------------------------------
    def delete(
        self,
        comment: Comment,
    ) -> None:

        self.db.delete(comment)

        self.db.flush()
