
import json
import re
import logging
from typing import Any

logger = logging.getLogger(__name__)

JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)

def safe_json_loads(text: str | None, default: Any = None) -> Any:
    if not text:
        return default or {}

    text = text.strip()

    # 1️⃣ Direct JSON
    try:
        return json.loads(text)
    except Exception:
        pass

    # 2️⃣ Extract first JSON object
    try:
        match = JSON_OBJECT_RE.search(text)
        if match:
            return json.loads(match.group(0))
    except Exception:
        pass

    logger.error(
        "safe_json_loads failed",
        extra={"raw": text},
    )

    return default or {}
