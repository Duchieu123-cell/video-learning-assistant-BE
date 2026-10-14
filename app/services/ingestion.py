import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.rag import LessonChunk
from app.services.chunking import TranscriptSegment, chunk_transcript
from app.services.embedding import get_embeddings_batch


async def ingest_lesson_transcript(
    db: AsyncSession,
    course_id: uuid.UUID,
    lesson_id: uuid.UUID,
    segments: list[TranscriptSegment]
) -> int:
    """
    Xử lý transcript của 1 bài học (lesson) và lưu vector vào PostgreSQL.
    Trả về số lượng chunks đã được lưu.
    """
    # 1. Cắt nhỏ transcript
    chunks_data = chunk_transcript(segments)
    if not chunks_data:
        return 0

    # 2. Tạo embeddings theo batch
    texts = [c.content for c in chunks_data]
    embeddings = get_embeddings_batch(texts)

    # 3. Tạo các bản ghi LessonChunk
    db_chunks = []
    for chunk, emb in zip(chunks_data, embeddings):
        db_chunk = LessonChunk(
            course_id=course_id,
            lesson_id=lesson_id,
            content=chunk.content,
            start_seconds=chunk.start_seconds,
            end_seconds=chunk.end_seconds,
            embedding=emb
        )
        db_chunks.append(db_chunk)

    # 4. Lưu vào cơ sở dữ liệu
    db.add_all(db_chunks)
    await db.commit()

    return len(db_chunks)