from models import UserConfig

DEFAULT_USER_CONFIG = {
    "enable_memory": False,
    "enable_multichat": False,
    "enable_chat_history": False,
    "enable_rag": False,
    "enable_tool": False,
    "max_sessions": 5,
    "max_tokens": 2048,
}

USER_CONFIG_CACHE = {}


def get_user_config(db, user_id: int) -> dict:
    # 1️⃣ Return from cache (DICT ONLY)
    if user_id in USER_CONFIG_CACHE:
        return USER_CONFIG_CACHE[user_id]

    # 2️⃣ Fetch from DB
    config = (
        db.query(UserConfig)
        .filter(UserConfig.user_id == user_id)
        .first()
    )

    # 3️⃣ Create default row if not exists
    if not config:
        config = UserConfig(
            user_id=user_id,
            **DEFAULT_USER_CONFIG
        )
        db.add(config)
        db.commit()
        db.refresh(config)

    # 4️⃣ ORM ➜ DICT (CRITICAL STEP)
    config_dict = {
        "enable_memory": bool(config.enable_memory),
        "enable_multichat": bool(config.enable_multichat),
        "enable_chat_history": bool(config.enable_chat_history),
        "enable_rag": bool(config.enable_rag),
        "enable_tool": bool(config.enable_tool),
        "max_sessions": int(config.max_sessions),
        "max_tokens": int(config.max_tokens),
    }

    # 5️⃣ Cache SAFE dict
    USER_CONFIG_CACHE[user_id] = config_dict

    return config_dict

