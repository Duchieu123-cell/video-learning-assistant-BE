
from app.core.config import settings
import httpx
import math

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-embedding-001:embedContent"
)

GEMINI_BATCH_API_URL = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-embedding-001:batchEmbedContents"
)

EMBEDDING_DIMENSION = 1536

HEADERS = {
    "x-goog-api-key": settings.GEMINI_API_KEY,
    "Content-Type": "application/json",
}

def validate_vector(data) -> list[float]:
    """Kiểm tra và chuẩn hóa embedding 1536 chiều."""
    if not isinstance(data, list):
        raise ValueError(
            "Embedding response phải là một list."
        )

    if len(data) != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Embedding phải có {EMBEDDING_DIMENSION} chiều, "
            f"nhưng nhận được {len(data)} chiều."
        )

    if not all(
        isinstance(x, (int, float))
        and not isinstance(x, bool)
        and math.isfinite(x)
        for x in data
    ):
        raise ValueError(
            "Embedding vector chứa giá trị không hợp lệ."
        )

    return [float(x) for x in data]


def clean_text(text: str) -> str:
    """Chuẩn hóa khoảng trắng trong văn bản."""
    return " ".join(text.split())

def build_embedding_request(
    text: str,
    task_type: str,
) -> dict:
    """Tạo phần request dùng chung cho Gemini Embedding API."""
    return {
        "content": {
            "parts": [{"text": text}]
        },
        "taskType": task_type,
        "outputDimensionality": EMBEDDING_DIMENSION,
    }


async def get_embedding(
    text: str,
    task_type: str = "RETRIEVAL_QUERY",
) -> list[float]:
    """Tạo embedding cho một văn bản hoặc câu hỏi."""
    text = clean_text(text)

    if not text:
        raise ValueError(
            "Văn bản đầu vào không được để trống."
        )

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            GEMINI_API_URL,
            headers=HEADERS,
            json=build_embedding_request(text, task_type),
        )

        if response.is_error:
            print("Gemini HTTP status:", response.status_code)
            print("Gemini response body:", response.text)

        response.raise_for_status()
        data = response.json()

    try:
        vector = data["embedding"]["values"]
    except (KeyError, TypeError) as exc:
        raise ValueError(
            "Gemini response không chứa embedding.values."
        ) from exc

    return validate_vector(vector)


async def get_embeddings_batch(
    texts: list[str],
    task_type: str = "RETRIEVAL_DOCUMENT",
) -> list[list[float]]:
    """Tạo embedding cho nhiều văn bản theo thứ tự đầu vào."""
    clean_texts = [clean_text(text) for text in texts]

    if not clean_texts:
        return []

    if any(not text for text in clean_texts):
        raise ValueError(
            "Danh sách chứa văn bản rỗng. "
            "Hãy xử lý chúng trước khi tạo embedding."
        )

    requests = [
        {
            "model": "models/gemini-embedding-001",
            **build_embedding_request(text, task_type),
        }
        for text in clean_texts
    ]

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            GEMINI_BATCH_API_URL,
            headers=HEADERS,
            json={"requests": requests},
        )

        if response.is_error:
            print("Gemini HTTP status:", response.status_code)
            print("Gemini response body:", response.text)

        response.raise_for_status()
        data = response.json()

    try:
        raw_embeddings = [
            item["values"]
            for item in data["embeddings"]
        ]
    except (KeyError, TypeError) as exc:
        raise ValueError(
            "Gemini batch response không hợp lệ."
        ) from exc

    if len(raw_embeddings) != len(clean_texts):
        raise ValueError(
            f"Số embedding ({len(raw_embeddings)}) không khớp "
            f"số văn bản ({len(clean_texts)})."
        )

    return [
        validate_vector(vector)
        for vector in raw_embeddings
    ]
