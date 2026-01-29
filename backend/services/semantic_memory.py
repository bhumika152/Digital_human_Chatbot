import torch
from typing import List, Tuple, Optional
from sentence_transformers.util import cos_sim
from models import MemoryStore


def find_best_semantic_match(
    memories: List[MemoryStore],
    query_embedding: List[float],
    threshold: float = 0.35,
) -> Tuple[Optional[MemoryStore], Optional[float]]:
    """
    Returns:
        (best_match_memory, similarity_score)
    """

    if not memories:
        return None, None

    # Convert query embedding once
    q = torch.tensor(query_embedding)

    best_match = None
    best_score = None

    for mem in memories:
        if not mem.embedding:
            continue

        mem_embedding = torch.tensor(mem.embedding)

        score = cos_sim(q, mem_embedding).item()

        if score >= threshold and (
            best_score is None or score > best_score
        ):
            best_score = score
            best_match = mem

    return best_match, best_score
