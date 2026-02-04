"""
Tests semantic search from knowledge base
WITHOUT digital human or agents.
"""

from services.knowledge_base_service import KnowledgeBaseService

def main():
    query = (
        "What is the District Export Promotion Committees - "
        "Institutional Mechanism at District Level?"
    )

    chunks = KnowledgeBaseService.read(
        query=query,
        limit=3,
        document_types=["POLICY"],
        industry="fintech",
    )

    print(f"\n🔍 Query: {query}")
    print(f"📄 Chunks found: {len(chunks)}\n")

    for i, c in enumerate(chunks, 1):
        print(f"--- Chunk {i} ---")
        print("Score:", c.get("score"))
        print("Text:", c.get("content", "")[:300])
        print()

    if not chunks:
        print("❌ RAG retrieval failed")
    else:
        print("✅ RAG retrieval working")

if __name__ == "__main__":
    main()
