import json
from collections.abc import AsyncGenerator
from google import genai
from google.genai import types
from app.core.config import settings
from app.schemas.rag import RetrievedChunk
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.models.rag import ChatHistory

client = genai.Client(api_key=settings.GEMINI_API_KEY)


def build_system_prompt(chunks: list[RetrievedChunk]) -> str:
    """Tạo system instruction kèm ngữ cảnh từ các chunk bài giảng."""
    context_text = "\n\n".join(
        [
            f"[Nguồn: {c.lesson_title} (giây {c.start_seconds} - {c.end_seconds})]:\n{c.content}"
            for c in chunks
        ]
    )

    return (
        "Bạn là trợ lý AI học tập chuyên nghiệp cho khóa học.\n"
        "Nhiệm vụ của bạn là giải đáp câu hỏi của học viên DỰA TRÊN ngữ cảnh bài giảng dưới đây.\n"
        "Nguyên tắc:\n"
        "1. Trả lời rõ ràng, sư phạm, có định dạng Markdown dễ nhìn.\n"
        "2. Nếu tài liệu bài giảng không đề cập hoặc thông tin không đủ, hãy trả lời trung thực là giáo trình chưa cung cấp phần này.\n"
        "3. Hãy nhắc đến mốc thời gian bài học nếu phù hợp để học viên tiện xem lại video.\n\n"
        f"--- TÀI LIỆU KHÓA HỌC ---\n{context_text}\n-------------------------"
    )


async def generate_rag_stream(
    chunks: list[RetrievedChunk],
    user_query: str,
    db: AsyncSession,
    course_id: uuid.UUID,
    user_id: uuid.UUID
) -> AsyncGenerator[str, None]:
    """Tạo luồng Server-Sent Events (SSE) trả về client."""
    # Gửi gói metadata citations trước tiên để client render các nút tua video
    citations = [
        {
            "chunk_id": str(c.chunk_id),
            "lesson_id": str(c.lesson_id),
            "lesson_title": c.lesson_title,
            "start_seconds": c.start_seconds,
            "end_seconds": c.end_seconds,
            "similarity_score": round(c.similarity_score, 3),
        }
        for c in chunks
    ]
    meta_packet = json.dumps({"type": "citations", "data": citations}, ensure_ascii=False)
    yield f"data: {meta_packet}\n\n"

    system_instruction = build_system_prompt(chunks)

    try:
        accumulated_response: list[str] = []
        
        async for chunk in await client.aio.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=user_query,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0,
            )
        ):
            if chunk.text:
                accumulated_response.append(chunk.text)
                payload = json.dumps({"type": "token", "data": chunk.text}, ensure_ascii=False)
                yield f"data: {payload}\n\n"

        chat_response_content = ("").join(accumulated_response)

        if chat_response_content.strip():
            new_user_chat = ChatHistory(
                id=uuid.uuid4(),
                course_id=course_id,
                user_id=user_id,
                role="user",
                content=user_query
            )
            
            new_ai_chat = ChatHistory(
                id=uuid.uuid4(),
                course_id=course_id,
                user_id=user_id,
                role="assistant",
                content=chat_response_content
            )
            
            db.add_all([new_user_chat, new_ai_chat])
            await db.flush()
        
        done_packet = json.dumps({"type": "done"}, ensure_ascii=False)
        yield f"data: {done_packet}\n\n"

    except Exception as e:
        err_packet = json.dumps({"type": "error", "message": str(e)}, ensure_ascii=False)
        yield f"data: {err_packet}\n\n"