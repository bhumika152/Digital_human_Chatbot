# backend/services/knowledge_base/kb_reranker.py

from sentence_transformers import CrossEncoder

# Load once at startup (IMPORTANT)
reranker_model = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


def rerank(query: str, candidates, top_k: int = 5):
    """
    Rerank ANN candidates using cross-encoder.
    candidates: List[(KnowledgeBaseEmbedding, score)]
    """

    if not candidates:
        return []

    pairs = [(query, r.content) for r, _ in candidates]
    scores = reranker_model.predict(pairs)

    reranked = sorted(
        zip(candidates, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [item[0][0] for item in reranked[:top_k]]
