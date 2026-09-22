
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.attachment import Attachment


class AttachmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, attachment_id: int) -> Attachment | None:
        statement = select(Attachment).where(
            Attachment.id == attachment_id
        )

        return self.db.scalar(statement)

    def get_by_ticket(
        self,
        ticket_id: int,
    ) -> list[Attachment]:

        statement = (
            select(Attachment)
            .where(Attachment.ticket_id == ticket_id)
            .order_by(Attachment.id.desc())
        )

        return list(self.db.scalars(statement).all())

    def create(
        self,
        attachment: Attachment,
    ) -> Attachment:

        self.db.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)

        return attachment

    def delete(
        self,
        attachment: Attachment,
    ) -> None:

        self.db.delete(attachment)
        self.db.commit()
        
        