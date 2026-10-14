import uuid
from app.models.rag import ChatHistory
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def get_chat_history(
    course_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession
):
    stmt = (
        select(ChatHistory)
        .where(ChatHistory.course_id == course_id, ChatHistory.user_id == user_id)
        .order_by(ChatHistory.created_at.asc())
    )
    
    result = await db.execute(stmt)
    return result.scalars().all()