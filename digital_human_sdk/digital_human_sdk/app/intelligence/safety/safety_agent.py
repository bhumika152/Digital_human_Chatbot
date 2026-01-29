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
    name="Safety Agent",
    instructions="""
You are a content safety checker.

Your task:
- Decide whether the user's message is SAFE or UNSAFE.

Respond ONLY in valid JSON.

SAFE content includes:
- General knowledge
- Education
- Casual conversation
- Harmless personal questions

UNSAFE content includes:
- Violence, murder, terrorism
- Illegal instructions
- Self-harm
- Hate speech
- Sexual content involving minors

JSON FORMAT:
{
  "safe": true | false,
  "reason": "short explanation if unsafe"
}

Rules:
- If SAFE → safe=true
- If UNSAFE → safe=false + reason
- Do NOT mention policies
""",
    model=get_model_name(),
)
