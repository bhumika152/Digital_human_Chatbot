# backend/services/knowledge_base/kb_semantic_search.py

import torch
from typing import List
from sentence_transformers.util import cos_sim
from models import KnowledgeBaseEmbedding


def semantic_search_kb(
    records: List[KnowledgeBaseEmbedding],
    query_embedding: list[float],
    top_k: int = 5,
    threshold: float = 0.35,
) -> List[tuple[KnowledgeBaseEmbedding, float]]:
    """
    Returns top-k KB chunks sorted by similarity score
    """

    if not records:
        return []

    q = torch.tensor(query_embedding)

    scored_results = []

    for record in records:
        if not record.embedding:
            continue

        emb = torch.tensor(record.embedding)
        score = cos_sim(q, emb).item()

        if score >= threshold:
            scored_results.append((record, score))

    # sort by similarity DESC
    scored_results.sort(key=lambda x: x[1], reverse=True)

    return scored_results[:top_k]
