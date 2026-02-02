from agents import Agent
from digital_human_sdk.app.intelligence.safety.contracts import SafetyResult
from digital_human_sdk.app.intelligence.models.litellm_model import get_model_name

# importing registers guardrails
from . import guardrails


def safety_response(safe: bool, reason: str | None):
    if safe:
        return SafetyResult(
            safe=True,
            message="OK",
        ).model_dump()

    return SafetyResult(
        safe=False,
        reason=reason,
        message="Sorry, I can’t help with that request.",
    ).model_dump()


safe_agent = Agent(
    name ="Safety_Agent",
    instructions="""
You are a content safety checker.

Your task:
- Decide whether the user's message is SAFE or UNSAFE.

You MUST respond ONLY in valid JSON.
No extra text. No markdown.

JSON format:
{
  "safe": true | false,
  "message": "string"
}

Rules:
- If SAFE:
  - safe = true
  - message = "OK"

- If UNSAFE:
  - safe = false
  - message = a short, polite, context-aware refusal
  - briefly explain why you can’t help
  - optionally redirect to a safe alternative
  - do NOT mention policies, rules, or internal systems

Tone:
- Calm
- Respectful
- Non-judgmental
""",
model = get_model_name(),

)