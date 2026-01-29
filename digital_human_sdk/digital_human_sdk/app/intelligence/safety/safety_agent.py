from agents import Agent
from .contracts import SafetyResult
from digital_human_sdk.app.intelligence.models.litellm_model import get_model_name

# Importing guardrails registers them
from . import guardrails
import litellm

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

You are a content safety checker.
 
Your task:

- Decide whether the user's message is SAFE or UNSAFE.
 
SAFE content includes:

- General knowledge (science, history, people)

- Weather questions

- Casual conversation

- Education, explanations, opinions

- Harmless personal questions
 
UNSAFE content includes:

- Violence, murder, terrorism

- Instructions for illegal activities

- Self-harm or suicide encouragement

- Hate speech or harassment

- Sexual content involving minors
 
Rules:

- If the message is SAFE, respond with: "SAFE"

- If the message is UNSAFE, respond with a short, polite refusal explaining that you cannot help with that request.

- Do NOT mention policies, rules, or internal systems.

- Do NOT block normal or harmless questions.

- Be calm and respectful.

""",

    model=get_model_name(),

)

 