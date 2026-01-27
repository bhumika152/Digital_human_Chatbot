from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(text: str) -> list[float]:
    if text is None:
        raise ValueError("Embedding text is None")

    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text)}")

    text = text.strip()
    if not text:
        raise ValueError("Embedding text is empty")

    return _model.encode(
        text,
        normalize_embeddings=True
    ).tolist()
