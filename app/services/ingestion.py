import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.rag import LessonChunk
from app.services.chunking import TranscriptSegment, chunk_transcript
from app.services.embedding import get_embeddings_batch
from app.services.transcription import transcribe_cloudinary_video
from app.core.database import AsyncSessionLocal


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

    # 2. Lọc các chunk không hợp lệ và tạo embeddings theo batch
    chunks_data = [c for c in chunks_data if c.content.strip()]
    if not chunks_data:
        return 0

    texts = [c.content for c in chunks_data]
    embeddings = await get_embeddings_batch(texts)

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

    db.add_all(db_chunks)
    await db.commit()

    return len(db_chunks)

async def process_video_rag(
    course_id: uuid.UUID,
    lesson_id: uuid.UUID,
    video_url: str,
):
    """:
    Tự động bóc tách phụ đề từ link Cloudinary và nạp vector vào DB.
    """
    try:
        print(f"Bắt đầu trích xuất phụ đề cho bài học {lesson_id}...")
        segments = await transcribe_cloudinary_video(video_url)

        if not segments:
            print(f"Không tìm thấy lời thoại nào trong video của bài học {lesson_id}")
            return

        async with AsyncSessionLocal() as db:
            chunks_count = await ingest_lesson_transcript(
                db=db,
                course_id=course_id,
                lesson_id=lesson_id,
                segments=segments,
            )
            print(f"Đã xử lý xong bài học {lesson_id}: {chunks_count} vector chunks đã được lưu")
            await db.close()

    except Exception as e:
        print(f"Lỗi khi xử lý RAG ngầm cho bài học {lesson_id}: {str(e)}")