from sklearn.metrics.pairwise import cosine_similarity

SIMILARITY_THRESHOLD = 0.82

def fetch_semantic_match(db, user_id, new_embedding):
    """
    Find most similar ACTIVE memory of SAME USER
    """
    rows = db.execute(
        """
        SELECT id, embedding
        FROM memory
        WHERE user_id = :user_id
          AND is_active = true
        """,
        {"user_id": user_id}
    ).fetchall()

    best_id = None
    best_score = 0.0

    for row in rows:
        score = cosine_similarity(
            [new_embedding],
            [row.embedding]
        )[0][0]

        if score > best_score:
            best_score = score
            best_id = row.id

    if best_score >= SIMILARITY_THRESHOLD:
        return best_id

    return None
