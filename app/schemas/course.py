import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class LessonResponse(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    title: str
    video_url: str | None
    duration_seconds: int
    order_index: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CourseDetailResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    instructor_id: uuid.UUID
    created_at: datetime
    lessons: list[LessonResponse] = []

    model_config = ConfigDict(from_attributes=True)


class CourseListItem(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)