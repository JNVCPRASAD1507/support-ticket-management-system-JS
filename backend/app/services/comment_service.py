from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.audit_actions import AuditAction
from app.models.comment import Comment
from app.models.ticket import Ticket
from app.repositories.comment_repository import CommentRepository
from app.schemas.comment import CommentCreate, CommentUpdate
from app.services.audit_log_service import create_audit_log
from app.services.notification_service import NotificationService


class CommentService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = CommentRepository(db)

    # ---------------------------------------------------------
    # GET SINGLE COMMENT
    # ---------------------------------------------------------
    def get_comment(
        self,
        comment_id: int,
    ) -> Comment:

        comment = self.repository.get_by_id(
            comment_id
        )

        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found",
            )

        return comment

    # ---------------------------------------------------------
    # GET TICKET COMMENTS
    # ---------------------------------------------------------
    def get_ticket_comments(
        self,
        ticket_id: int,
    ) -> list[Comment]:

        ticket = self.db.get(
            Ticket,
            ticket_id,
        )

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        return self.repository.get_by_ticket(
            ticket_id
        )

    # ---------------------------------------------------------
    # CREATE COMMENT
    # ---------------------------------------------------------
    def create_comment(
        self,
        ticket_id: int,
        data: CommentCreate,
        current_user_id: int,
    ) -> Comment:

        ticket = self.db.get(
            Ticket,
            ticket_id,
        )

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

        comment = self.repository.create(
            comment
        )

        # -----------------------------------------------------
        # AUDIT: COMMENT CREATED
        # -----------------------------------------------------
        create_audit_log(
            self.db,
            user_id=current_user_id,
            action=AuditAction.COMMENT_CREATED,
            entity_type="Comment",
            entity_id=comment.id,
            description=(
                f"Comment was added to "
                f"ticket '{ticket.ticket_number}'"
            ),
            new_value=comment.content,
        )

        recipients = {ticket.created_by_id}
        if ticket.assigned_to_id is not None:
            recipients.add(ticket.assigned_to_id)
        recipients.discard(current_user_id)
        notification_service = NotificationService(self.db)
        for user_id in recipients:
            notification_service.create_notification(
                user_id=user_id,
                title="New Ticket Comment",
                message=f"A new comment was added to ticket {ticket.ticket_number}.",
                notification_type="comment_created",
            )

        self.db.commit()
        self.db.refresh(comment)

        return comment

    # ---------------------------------------------------------
    # UPDATE COMMENT
    # ---------------------------------------------------------
    def update_comment(
        self,
        comment_id: int,
        data: CommentUpdate,
        current_user_id: int,
    ) -> Comment:

        comment = self.get_comment(
            comment_id
        )

        if comment.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own comments",
            )

        old_content = comment.content
        new_content = data.content.strip()

        comment.content = new_content

        comment = self.repository.update(
            comment
        )

        # -----------------------------------------------------
        # AUDIT: COMMENT UPDATED
        # -----------------------------------------------------
        create_audit_log(
            self.db,
            user_id=current_user_id,
            action=AuditAction.COMMENT_UPDATED,
            entity_type="Comment",
            entity_id=comment.id,
            description=(
                f"Comment {comment.id} was updated"
            ),
            old_value=old_content,
            new_value=new_content,
        )

        self.db.commit()
        self.db.refresh(comment)

        return comment

    # ---------------------------------------------------------
    # DELETE COMMENT
    # ---------------------------------------------------------
    def delete_comment(
        self,
        comment_id: int,
        current_user_id: int,
    ) -> None:

        comment = self.get_comment(
            comment_id
        )

        if comment.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own comments",
            )

        # Store values before deletion
        deleted_comment_id = comment.id
        deleted_content = comment.content
        ticket_id = comment.ticket_id

        self.repository.delete(
            comment
        )

        # -----------------------------------------------------
        # AUDIT: COMMENT DELETED
        # -----------------------------------------------------
        create_audit_log(
            self.db,
            user_id=current_user_id,
            action=AuditAction.COMMENT_DELETED,
            entity_type="Comment",
            entity_id=deleted_comment_id,
            description=(
                f"Comment {deleted_comment_id} "
                f"was deleted from ticket {ticket_id}"
            ),
            old_value=deleted_content,
        )

        self.db.commit()