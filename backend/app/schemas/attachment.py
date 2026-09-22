
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AttachmentResponse(BaseModel):
    id: int
    ticket_id: int
    uploaded_by_id: int
    filename: str
    stored_filename: str
    file_path: str
    content_type: str
    file_size: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
    