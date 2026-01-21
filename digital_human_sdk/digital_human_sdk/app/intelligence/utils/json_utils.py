# import json
# import re
# import logging

# logger = logging.getLogger(__name__)

# def safe_json_loads(text: str, default=None):
#     if not text:
#         return default or {}

#     try:
#         # Remove ```json and ``` fences if present
#         cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE)
#         return json.loads(cleaned)
#     except Exception as e:
#         logger.error(f"safe_json_loads failed: {e} | raw={text}")
#         return default or {}
import json
import re
import logging
from typing import Any

logger = logging.getLogger(__name__)

JSON_BLOCK_RE = re.compile(
    r"```(?:json)?\s*(\{.*?\})\s*```",
    re.DOTALL | re.IGNORECASE,
)

def safe_json_loads(text: str | None, default: Any = None) -> Any:
    if not text:
        return default or {}

    text = text.strip()

    try:
        # 1️⃣ Try direct JSON first
        return json.loads(text)
    except Exception:
        pass

    try:
        # 2️⃣ Try extracting JSON from markdown block
        match = JSON_BLOCK_RE.search(text)
        if match:
            return json.loads(match.group(1))
    except Exception:
        pass

    try:
        # 3️⃣ Last attempt: remove fences blindly
        cleaned = re.sub(r"```(?:json)?|```", "", text).strip()
        return json.loads(cleaned)
    except Exception as e:
        logger.error(
            "safe_json_loads failed",
            extra={"error": str(e), "raw": text},
        )
        return default or {}