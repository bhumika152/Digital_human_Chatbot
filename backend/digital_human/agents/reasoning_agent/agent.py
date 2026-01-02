# reasoning_agent/agent.py

from digital_human.graph.state import AgentState
from digital_human.agents.reasoning_agent.prompts import REASONING_PROMPT
from digital_human.agents.reasoning_agent.schemas import ReasoningOutput
from openai import OpenAI
import json

client = OpenAI()


def reasoning_agent(state: AgentState) -> AgentState:
    """
    Reasoning Agent
    ----------------
    Uses OpenAI to infer user intent and confidence.
    """

    prompt = REASONING_PROMPT + f'\nUser message:\n"{state.user_input}"'



    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a precise reasoning engine."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    content = response.choices[0].message.content

    try:
        parsed = ReasoningOutput(**json.loads(content))
    except Exception:
        # Safe fallback
        state.intent = {"type": "general_chat"}
        state.intent_confidence = 0.3
        return state

    state.intent = {
        "type": parsed.intent_type,
        "topic": parsed.topic
    }
    state.intent_confidence = parsed.confidence

    return state
