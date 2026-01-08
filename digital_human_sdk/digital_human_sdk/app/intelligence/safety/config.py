import re

# ❌ Disallowed patterns (prompt injection, hacking, policy bypass)
DISALLOWED_PATTERNS = [
    r"ignore previous instructions",
    r"system prompt",
    r"developer message",
    r"jailbreak",
    r"bypass",
    r"hack",
    r"exploit",
]

# ❌ Blocked topics
BLOCKED_TOPICS = [
    "violence",
    "self-harm",
    "terrorism",
    "illegal drugs",
]

# ✅ Max output size (anti data exfiltration)
MAX_OUTPUT_CHARS = 800

# ✅ Allowed tools (deny-by-default)
ALLOWED_TOOLS = {
    "safe_calculator",
}


def matches_blocked_pattern(text: str) -> bool:
    text = text.lower()
    return any(re.search(p, text) for p in DISALLOWED_PATTERNS)


