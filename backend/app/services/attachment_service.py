
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.attachment import Attachment
from app.models.ticket import Ticket
from app.repositories.attachment_repository import AttachmentRepository
from app.utils.file_validation import validate_file


ATTACHMENT_DIRECTORY = Path("storage/attachments")


class AttachmentService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = AttachmentRepository(db)

        ATTACHMENT_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

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

        return self.repository.get_by_ticket(ticket_id)

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

        content = await validate_file(file)

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

        file_path.write_bytes(content)

        attachment = Attachment(
            ticket_id=ticket_id,
            uploaded_by_id=current_user_id,
            filename=original_filename,
            stored_filename=stored_filename,
            file_path=str(file_path),
            content_type=file.content_type
            or "application/octet-stream",
            file_size=len(content),
        )

        try:
            return self.repository.create(
                attachment
            )

        except Exception:
            if file_path.exists():
                file_path.unlink()

            raise

    def delete_attachment(
        self,
        attachment_id: int,
        current_user_id: int,
    ) -> None:

        attachment = self.get_attachment(
            attachment_id
        )

        if attachment.uploaded_by_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own attachments",
            )

        file_path = Path(
            attachment.file_path
        )

        self.repository.delete(attachment)

        if file_path.exists():
            file_path.unlink()
            
    
    