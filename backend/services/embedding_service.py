from sentence_transformers import SentenceTransformer

# Load once at startup
_model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text: str) -> list[float]:
    """
    Convert text → semantic vector (NO BRAIN, NO API)
    """
    return _model.encode(text).tolist()
