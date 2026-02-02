# backend/services/knowledge_base/kb_embedding_service.py

from services.embedding_service import get_embedding


def get_kb_embedding(text: str) -> list[float]:
    """
    Generate embedding for admin knowledge base content
    (FAQ, Policy, Terms, etc.)
    """
    return get_embedding(text)
