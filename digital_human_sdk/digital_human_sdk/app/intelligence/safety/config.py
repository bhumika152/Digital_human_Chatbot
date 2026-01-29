import re

# ❌ VERY STRICT injection patterns (phrases only)
DISALLOWED_PATTERNS = [
    r"ignore\s+previous\s+instructions",
    r"reveal\s+system\s+prompt",
    r"developer\s+message",
    r"jailbreak\s+the\s+model",
    r"bypass\s+ai\s+safety",
]

# ❌ Dangerous domains (used WITH intent words)
BLOCKED_TOPICS = [
    "bomb",
    "weapon",
    "self-harm",
    "terrorist attack",
    "illegal drugs",
]

MAX_OUTPUT_CHARS = 800


def matches_blocked_pattern(text: str) -> bool:
    return any(re.search(p, text) for p in DISALLOWED_PATTERNS)
