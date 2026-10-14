import uuid
from pydantic import BaseModel


class RetrievedChunk(BaseModel):
    chunk_id: uuid.UUID
    lesson_id: uuid.UUID
    lesson_title: str
    content: str
    start_seconds: int | None
    end_seconds: int | None
    similarity_score: float