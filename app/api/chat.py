from fastapi import APIRouter, HTTPException, status, Path
from fastapi.responses import StreamingResponse
from app.core.dependencies import DBSession, CurrentUser
from app.schemas.chat import ChatStreamRequest, ChatMessageResponse
from app.services.retrieval import retrieve_relevant_chunks
from app.services.generation import generate_rag_stream
from typing import Annotated
import uuid
from app.services.history import get_chat_history

router = APIRouter(
    prefix="/chat",
    tags=["RAG Chat"]
)


@router.post("/stream")
async def stream_chat_response(
    req: ChatStreamRequest,
    current_user: CurrentUser,
    db: DBSession
):
    if not req.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Câu hỏi không được để trống"
        )

    chunks = await retrieve_relevant_chunks(
        db=db,
        course_id=req.course_id,
        query_text=req.query,
        top_k=3,
        similarity_threshold=0.3
    )

    return StreamingResponse(
        generate_rag_stream(
            chunks=chunks,
            user_query=req.query,
            db=db,
            course_id=req.course_id,
            user_id=current_user.id
        ),
        media_type="text/event-stream",
        headers={
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
    
    
@router.post("/history/{course_id}", response_model=list[ChatMessageResponse])
async def get_chat_history_endpoint(
    course_id: Annotated[uuid.UUID, Path()],
    current_user: CurrentUser,
    db: DBSession
):
    return await get_chat_history(course_id=course_id, user_id=current_user.id, db=db)