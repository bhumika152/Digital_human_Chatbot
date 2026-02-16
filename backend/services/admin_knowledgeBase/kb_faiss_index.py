# # backend/services/knowledge_base/kb_faiss_index.py

# import faiss
# import numpy as np
# from sqlalchemy.orm import Session
# from models import KnowledgeBaseEmbedding


# class KBVectorIndex:
#     """
#     FAISS HNSW index for cosine similarity search.
#     """

#     def __init__(self):
#         self.index = None
#         self.id_map = []

#     def build(self, db: Session):
#         records = (
#             db.query(KnowledgeBaseEmbedding)
#             .filter(KnowledgeBaseEmbedding.is_active.is_(True))
#             .all()
#         )

#         if not records:
#             return

#         embeddings = np.array(
#             [r.embedding for r in records],
#             dtype="float32",
#         )

#         # Normalize for cosine similarity
#         faiss.normalize_L2(embeddings)

#         dimension = embeddings.shape[1]

#         self.index = faiss.IndexHNSWFlat(
#             dimension,
#             32,
#             faiss.METRIC_INNER_PRODUCT,  # cosine via normalized dot product
#         )

#         self.index.hnsw.efConstruction = 40
#         self.index.add(embeddings)

#         self.id_map = records

#     def search(self, query_embedding: list[float], top_k: int = 20):
#         if self.index is None:
#             return []

#         query = np.array([query_embedding], dtype="float32")

#         # Normalize query
#         faiss.normalize_L2(query)

#         distances, indices = self.index.search(query, top_k)

#         results = []

#         for idx, score in zip(indices[0], distances[0]):
#             if idx == -1:
#                 continue
#             results.append((self.id_map[idx], float(score)))

#         return results
# backend/services/knowledge_base/kb_faiss_index.py

import faiss
import numpy as np
from sqlalchemy.orm import Session
from models import KnowledgeBaseEmbedding

EMBEDDING_DIM = 384


class KBVectorIndex:
    """
    FAISS Index for Knowledge Base using cosine similarity
    via normalized inner product.
    """

    def __init__(self):
        self.index = faiss.IndexIDMap2(
            faiss.IndexFlatIP(EMBEDDING_DIM)
        )

    def build(self, db: Session):

        records = (
            db.query(KnowledgeBaseEmbedding)
            .filter(KnowledgeBaseEmbedding.is_active.is_(True))
            .all()
        )

        if not records:
            return

        vectors = []
        ids = []

        for r in records:
            if not r.embedding:
                continue

            vectors.append(r.embedding)
            ids.append(r.kb_id)

        if not vectors:
            return

        vec = np.array(vectors).astype("float32")

        # 🔥 CRITICAL for cosine similarity
        faiss.normalize_L2(vec)

        ids = np.array(ids).astype("int64")

        self.index.add_with_ids(vec, ids)

        print("✅ KB FAISS built | total vectors:", self.index.ntotal)

    def search(self, query_embedding, top_k=20):

        if self.index.ntotal == 0:
            return []

        q = np.array([query_embedding]).astype("float32")

        # 🔥 MUST normalize query
        faiss.normalize_L2(q)

        scores, ids = self.index.search(q, top_k)

        results = []

        for score, kb_id in zip(scores[0], ids[0]):
            if kb_id != -1:
                results.append((int(kb_id), float(score)))

        return results
