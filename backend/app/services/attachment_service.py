from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.audit_actions import AuditAction
from app.models.attachment import Attachment
from app.models.ticket import Ticket
from app.repositories.attachment_repository import AttachmentRepository
from app.services.audit_log_service import create_audit_log
from app.services.notification_service import NotificationService
from app.utils.file_validation import validate_file


ATTACHMENT_DIRECTORY = Path(
    "storage/attachments"
)


class AttachmentService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = AttachmentRepository(db)

        ATTACHMENT_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ---------------------------------------------------------
    # GET SINGLE ATTACHMENT
    # ---------------------------------------------------------
    def get_attachment(
        self,
        attachment_id: int,
    ) -> Attachment:

        attachment = self.repository.get_by_id(
            attachment_id
        )

        if not attachment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found",
            )

        return attachment

    # ---------------------------------------------------------
    # GET TICKET ATTACHMENTS
    # ---------------------------------------------------------
    def get_ticket_attachments(
        self,
        ticket_id: int,
    ) -> list[Attachment]:

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
    # UPLOAD ATTACHMENT
    # ---------------------------------------------------------
    async def upload_attachment(
        self,
        ticket_id: int,
        file: UploadFile,
        current_user_id: int,
    ) -> Attachment:

        ticket = self.db.get(
            Ticket,
            ticket_id,
        )

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        # -----------------------------------------------------
        # VALIDATE FILE
        # -----------------------------------------------------
        content = await validate_file(
            file
        )

        original_filename = Path(
            file.filename
        ).name

        extension = Path(
            original_filename
        ).suffix

        stored_filename = (
            f"{uuid4().hex}{extension}"
        )

        file_path = (
            ATTACHMENT_DIRECTORY
            / stored_filename
        )

        # -----------------------------------------------------
        # SAVE FILE TO STORAGE
        # -----------------------------------------------------
        file_path.write_bytes(
            content
        )

        # -----------------------------------------------------
        # CREATE ATTACHMENT
        # -----------------------------------------------------
        attachment = Attachment(
            ticket_id=ticket_id,
            uploaded_by_id=current_user_id,
            filename=original_filename,
            stored_filename=stored_filename,
            file_path=str(file_path),
            content_type=(
                file.content_type
                or "application/octet-stream"
            ),
            file_size=len(content),
        )

        try:

            attachment = self.repository.create(
                attachment
            )

            # -------------------------------------------------
            # AUDIT: ATTACHMENT CREATED
            # -------------------------------------------------
            create_audit_log(
                self.db,
                user_id=current_user_id,
                action=AuditAction.ATTACHMENT_CREATED,
                entity_type="Attachment",
                entity_id=attachment.id,
                description=(
                    f"Attachment '{attachment.filename}' "
                    f"was uploaded to ticket "
                    f"'{ticket.ticket_number}'"
                ),
                new_value=attachment.filename,
            )

            recipients = {ticket.created_by_id}
            if ticket.assigned_to_id is not None:
                recipients.add(ticket.assigned_to_id)
            recipients.discard(current_user_id)
            notification_service = NotificationService(self.db)
            for user_id in recipients:
                notification_service.create_notification(
                    user_id=user_id,
                    title="New Ticket Attachment",
                    message=f"A new attachment was added to ticket {ticket.ticket_number}.",
                    notification_type="attachment_created",
                )

            self.db.commit()
            self.db.refresh(attachment)

            return attachment

        except Exception:

            # Remove physical file if database operation fails
            if file_path.exists():
                file_path.unlink()

            raise

    # ---------------------------------------------------------
    # DELETE ATTACHMENT
    # ---------------------------------------------------------
    def delete_attachment(
        self,
        attachment_id: int,
        current_user_id: int,
    ) -> None:

        attachment = self.get_attachment(
            attachment_id
        )

        # -----------------------------------------------------
        # AUTHORIZATION
        # -----------------------------------------------------
        if attachment.uploaded_by_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You can only delete "
                    "your own attachments"
                ),
            )

        # Store values before deletion
        deleted_attachment_id = attachment.id
        deleted_filename = attachment.filename
        ticket_id = attachment.ticket_id
        file_path = Path(
            attachment.file_path
        )

        # -----------------------------------------------------
        # DELETE DATABASE RECORD
        # -----------------------------------------------------
        self.repository.delete(
            attachment
        )

        # -----------------------------------------------------
        # AUDIT: ATTACHMENT DELETED
        # -----------------------------------------------------
        create_audit_log(
            self.db,
            user_id=current_user_id,
            action=AuditAction.ATTACHMENT_DELETED,
            entity_type="Attachment",
            entity_id=deleted_attachment_id,
            description=(
                f"Attachment '{deleted_filename}' "
                f"was deleted from ticket {ticket_id}"
            ),
            old_value=deleted_filename,
        )

        self.db.commit()

        # -----------------------------------------------------
        # DELETE PHYSICAL FILE
        # -----------------------------------------------------
        if file_path.exists():
            file_path.unlink()
            
            
    