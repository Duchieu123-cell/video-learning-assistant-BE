from sentence_transformers import SentenceTransformer

_model = None


def get_model() -> SentenceTransformer:
    """Lấy model embedding (tạo 1 lần duy nhất)."""
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def get_embedding(text: str) -> list[float]:
    """Tạo embedding cho 1 đoạn text (dùng khi user hỏi)."""
    model = get_model()
    clean_text = text.replace("\n", " ").strip()
    embedding = model.encode(clean_text, normalize_embeddings=True)
    return embedding.tolist()


def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Tạo embedding hàng loạt cho danh sách text (dùng khi ingest transcript)."""
    model = get_model()
    clean_texts = [t.replace("\n", " ").strip() for t in texts if t.strip()]
    if not clean_texts:
        return []

    embeddings = model.encode(clean_texts, normalize_embeddings=True, batch_size=32)
    return [emb.tolist() for emb in embeddings]