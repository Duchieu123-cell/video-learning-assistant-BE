import httpx
from groq import AsyncGroq
from app.core.config import settings
from app.services.chunking import TranscriptSegment

groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)


def convert_cloudinary_video_to_audio_url(video_url: str) -> str:
    """
    Chuyển đổi URL video Cloudinary (.mp4) sang URL audio (.mp3)
    với tham số nén bitrate 32k (br_32k) để file siêu nhẹ (< 10MB cho 30 phút).
    """
    audio_url = video_url.replace(".mp4", ".mp3").replace("/video/upload/", "/video/upload/br_32k/")

    return audio_url


async def transcribe_cloudinary_video(video_url: str) -> list[TranscriptSegment]:
    """
    Tải file audio đã được Cloudinary chuyển đổi và gửi sang Groq Whisper API
    để nhận về danh sách câu thoại kèm start_seconds, end_seconds.
    """
    audio_url = convert_cloudinary_video_to_audio_url(video_url)

    async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as http_client:
        response = await http_client.get(audio_url)
        response.raise_for_status()
        audio_bytes = response.content

    transcription = await groq_client.audio.transcriptions.create(
        file=("lesson_audio.mp3", audio_bytes),
        model="whisper-large-v3-turbo",
        response_format="verbose_json",
        temperature=0.0,
    )


    segments: list[TranscriptSegment] = []
    raw_segments = getattr(transcription, "segments", []) or []

    for seg in raw_segments:
        # Hỗ trợ cả trường hợp seg là dict hoặc object từ SDK
        start_time = seg["start"] if isinstance(seg, dict) else seg.start
        end_time = seg["end"] if isinstance(seg, dict) else seg.end
        text_content = seg["text"] if isinstance(seg, dict) else seg.text

        clean_text = text_content.strip()
        if clean_text:
            segments.append(
                TranscriptSegment(
                    start=int(start_time),
                    end=int(end_time),
                    text=clean_text,
                )
            )

    return segments