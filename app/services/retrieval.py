import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.course import Lesson
from app.models.rag import LessonChunk
from app.schemas.rag import RetrievedChunk
from app.services.embedding import get_embedding


async def retrieve_relevant_chunks(
    db: AsyncSession,
    course_id: uuid.UUID,
    query_text: str,
    top_k: int = 3,
    similarity_threshold: float = 0.35,  # Loại bỏ các đoạn context quá xa lạ với câu hỏi
) -> list[RetrievedChunk]:
    """
    1. Tạo vector embedding cho câu hỏi.
    2. Truy vấn Cosine Distance trên PostgreSQL trong phạm vi course_id.
    3. Join với bảng Lesson để lấy tiêu đề bài học tương ứng.
    """
    # 1. Tạo embedding câu hỏi (384 chiều)
    query_vector = get_embedding(query_text)

    # 2. Xây dựng query với pgvector cosine distance: embedding <=> query_vector
    # Độ tương đồng cosine similarity = 1 - cosine_distance
    cosine_distance = LessonChunk.embedding.cosine_distance(query_vector)
    similarity = (1 - cosine_distance).label("similarity_score")

    stmt = (
        select(
            LessonChunk.id.label("chunk_id"),
            LessonChunk.lesson_id,
            Lesson.title.label("lesson_title"),
            LessonChunk.content,
            LessonChunk.start_seconds,
            LessonChunk.end_seconds,
            similarity,
        )
        .join(Lesson, Lesson.id == LessonChunk.lesson_id)
        .where(LessonChunk.course_id == course_id)
        .order_by(cosine_distance.asc())
        .limit(top_k)
    )
    
    result = await db.execute(stmt)
    rows = result.all()

    # 3. Lọc theo ngưỡng similarity và map sang Pydantic schema
    retrieved_items: list[RetrievedChunk] = []
    for row in rows:
        if row.similarity_score >= similarity_threshold:
            retrieved_items.append(
                RetrievedChunk(
                    chunk_id=row.chunk_id,
                    lesson_id=row.lesson_id,
                    lesson_title=row.lesson_title,
                    content=row.content,
                    start_seconds=row.start_seconds,
                    end_seconds=row.end_seconds,
                    similarity_score=float(row.similarity_score),
                )
            )

    return retrieved_items