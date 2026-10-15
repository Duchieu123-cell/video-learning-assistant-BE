import math
from google import genai
from google.genai import types
from app.core.config import settings

# Khởi tạo client (tự động đọc biến môi trường GEMINI_API_KEY)
client = genai.Client(api_key=settings.GEMINI_API_KEY)

EMBEDDING_MODEL = "gemini-embedding-001"
# Có thể chọn 768, 1536 hoặc 3072 (mặc định của gemini-embedding-001 là 3072).
OUTPUT_DIMENSIONALITY = 768


def _normalize_l2(vec: list[float]) -> list[float]:
    """Chuẩn hóa vector (L2 normalization) tương đương normalize_embeddings=True."""
    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0.0:
        return vec
    return [x / norm for x in vec]


async def get_embedding(text: str) -> list[float]:
    """Tạo embedding bất đồng bộ cho 1 đoạn text (dùng khi user hỏi)."""
    clean_text = text.replace("\n", " ").strip()
    if not clean_text:
        return []

    response = await client.aio.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=clean_text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=OUTPUT_DIMENSIONALITY,
        ),
    )
    
    embedding = response.embeddings[0].values
    return _normalize_l2(embedding)


async def get_embeddings_batch(texts: list[str], batch_size: int = 100) -> list[list[float]]:
    """Tạo embedding hàng loạt bất đồng bộ (dùng khi ingest transcript)."""
    clean_texts = [t.replace("\n", " ").strip() for t in texts if t.strip()]
    if not clean_texts:
        return []

    all_embeddings: list[list[float]] = []

    # Chia nhỏ theo batch (API của Google hỗ trợ tối đa 100 đoạn text mỗi lần gọi)
    for i in range(0, len(clean_texts), batch_size):
        batch = clean_texts[i : i + batch_size]
        response = await client.aio.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=batch,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=OUTPUT_DIMENSIONALITY,
            ),
        )
        for emb in response.embeddings:
            all_embeddings.append(_normalize_l2(emb.values))

    return all_embeddings