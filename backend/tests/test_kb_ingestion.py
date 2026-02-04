"""
Run this file manually to verify:
- PDFs are ingested
- Embeddings exist
- Records are queryable
"""

from database import SessionLocal
from models import KnowledgeBaseEmbedding

def main():
    db = SessionLocal()

    try:
        docs = (
            db.query(KnowledgeBaseEmbedding)
            .filter(KnowledgeBaseEmbedding.document_type == "POLICY")
            .all()
        )

        print(f"\n📚 POLICY documents found: {len(docs)}\n")

        for d in docs[:5]:
            print("--------------------------------------------------")
            print("ID:", d.id)
            print("Title:", d.title)
            print("Industry:", d.industry)
            print("Has embedding:", bool(d.embedding))
            print("Content preview:", d.content[:200])
            print("--------------------------------------------------")

        if not docs:
            print("❌ No policy documents found. Ingestion failed.")
        else:
            print("✅ Policy documents look good.")

    finally:
        db.close()

if __name__ == "__main__":
    main()
