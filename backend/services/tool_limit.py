from fastapi import HTTPException

def ensure_tool_row(db, user_id: int, tool_name: str):
    db.execute(
        """
        INSERT INTO tool_usage (user_id, tool_name)
        VALUES (%s, %s)
        ON CONFLICT (user_id, tool_name) DO NOTHING
        """,
        (user_id, tool_name)
    )
    db.commit()


def check_tool_limit(db, user_id: int, tool_name: str) -> int:
    ensure_tool_row(db, user_id, tool_name)

    row = db.execute(
        """
        SELECT remaining_count
        FROM tool_usage
        WHERE user_id = %s AND tool_name = %s
        """,
        (user_id, tool_name)
    ).fetchone()

    if row["remaining_count"] <= 0:
        raise HTTPException(
            status_code=403,
            detail=f"{tool_name} tool limit reached"
        )

    return row["remaining_count"]
