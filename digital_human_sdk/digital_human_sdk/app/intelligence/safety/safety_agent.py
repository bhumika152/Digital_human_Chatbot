from agents import Agent
from .contracts import SafetyResult
from digital_human_sdk.app.intelligence.models.litellm_model import get_model_name

# Importing guardrails registers them
from . import guardrails


def safety_response(safe: bool, reason: str | None):
    if safe:
        return SafetyResult(
            safe=True,
            message="OK"
        ).model_dump()

    return SafetyResult(
        safe=False,
        reason=reason,
        message="Sorry, I can’t help with that request."
        ).model_dump()
safe_agent = Agent(
    name="Safety Agent",
    instructions="""
You are a safety gate for an AI assistant.

Task:
- Analyze the user message
- Decide if it is allowed or disallowed

Disallowed content includes:
- Illegal activities (drugs, weapons, fraud)
- Violence
- Self-harm
- Sexual exploitation
- Hate or harassment

Output STRICT JSON ONLY.

Allowed output formats:

If SAFE:
{
  "safe": true
}

If UNSAFE:
{
  "safe": false,
  "message": "A short polite refusal message for the user"
}

Rules:
- Never explain policies
- Never add extra text
""",
    model=get_model_name(),
)
