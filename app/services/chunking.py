from pydantic import BaseModel


class TranscriptSegment(BaseModel):
    start: int  # giây bắt đầu
    end: int    # giây kết thúc
    text: str


class ProcessedChunk(BaseModel):
    content: str
    start_seconds: int
    end_seconds: int


def chunk_transcript(
    segments: list[TranscriptSegment],
    target_chunk_length: int = 400
) -> list[ProcessedChunk]:
    """
    Gom các transcript segments nhỏ thành các chunk có ngữ cảnh đầy đủ,
    đồng thời giữ được mốc thời gian bắt đầu và kết thúc của chunk đó.
    """
    chunks: list[ProcessedChunk] = []
    
    current_text_parts: list[str] = []
    current_start: int | None = None
    current_end: int = 0
    current_length = 0

    for seg in segments:
        clean_text = seg.text.strip()
        if not clean_text:
            continue

        if current_start is None:
            current_start = seg.start

        current_text_parts.append(clean_text)
        current_end = seg.end
        current_length += len(clean_text) + 1

        # Khi vượt ngưỡng target_chunk_length thì đóng gói thành 1 chunk
        if current_length >= target_chunk_length:
            chunks.append(
                ProcessedChunk(
                    content=" ".join(current_text_parts),
                    start_seconds=current_start,
                    end_seconds=current_end
                )
            )
            # Reset cho chunk tiếp theo
            current_text_parts = []
            current_start = None
            current_length = 0

    # Lưu nốt phần còn sót lại cuối cùng
    if current_text_parts and current_start is not None:
        chunks.append(
            ProcessedChunk(
                content=" ".join(current_text_parts),
                start_seconds=current_start,
                end_seconds=current_end
            )
        )

    return chunks