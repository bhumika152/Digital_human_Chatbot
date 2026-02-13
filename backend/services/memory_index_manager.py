# services/memory_index_manager.py

import faiss
import numpy as np
from typing import Dict

EMBEDDING_DIM = 384  # change if needed


class MemoryIndexManager:
    def __init__(self):
        self.user_indexes: Dict[int, faiss.IndexIDMap2] = {}

    def _create_index(self):
        return faiss.IndexIDMap2(
            faiss.IndexFlatIP(EMBEDDING_DIM)
        )

    def get_user_index(self, user_id: int):
        if user_id not in self.user_indexes:
            self.user_indexes[user_id] = self._create_index()
        return self.user_indexes[user_id]

    def add(self, user_id: int, memory_id: int, embedding):
        index = self.get_user_index(user_id)
        vec = np.array([embedding]).astype("float32")
        faiss.normalize_L2(vec)
        index.add_with_ids(vec, np.array([memory_id]))

    def search(self, user_id: int, query_embedding, top_k=5):
        if user_id not in self.user_indexes:
            return []

        index = self.user_indexes[user_id]

        if index.ntotal == 0:
            return []

        q = np.array([query_embedding]).astype("float32")
        faiss.normalize_L2(q)

        scores, ids = index.search(q, top_k)

        results = []
        for score, mid in zip(scores[0], ids[0]):
            if mid != -1:
                results.append((int(mid), float(score)))

        return results

    def remove(self, user_id: int, memory_id: int):
        if user_id in self.user_indexes:
            self.user_indexes[user_id].remove_ids(
                np.array([memory_id])
            )


# Global singleton
memory_index_manager = MemoryIndexManager()
