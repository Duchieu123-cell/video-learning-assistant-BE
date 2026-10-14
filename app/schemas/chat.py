import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ChatStreamRequest(BaseModel):
    course_id: uuid.UUID
    query: str


class ChatMessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)