from sqlalchemy.orm import Session
from models import VectorDBRAG
def store_embedding(
    db: Session,
    user_id: int,
    embedding: list[float],
    metadata: dict
):
    doc = VectorDBRAG(
        user_id=user_id,
        embedding=embedding,
        meta_data=metadata
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc
def get_user_embeddings(db: Session, user_id: int):
    return (
        db.query(VectorDBRAG)
        .filter(VectorDBRAG.user_id == user_id)
        .all()
    )
