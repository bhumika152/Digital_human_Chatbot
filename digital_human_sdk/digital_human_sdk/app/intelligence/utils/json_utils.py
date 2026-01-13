import json
import re
import logging

logger = logging.getLogger(__name__)

def safe_json_loads(text: str, default=None):
    if not text:
        return default or {}

    try:
        # Remove ```json and ``` fences if present
        cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE)
        return json.loads(cleaned)
    except Exception as e:
        logger.error(f"safe_json_loads failed: {e} | raw={text}")
        return default or {}
