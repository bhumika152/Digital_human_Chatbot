# # services/semantic_memory.py

from services.memory_index_manager import memory_index_manager


def search_semantic_memory(
    user_id: int,
    query_embedding,
    top_k: int = 5,
):
    return memory_index_manager.search(
        user_id=user_id,
        query_embedding=query_embedding,
        top_k=top_k,
    )
