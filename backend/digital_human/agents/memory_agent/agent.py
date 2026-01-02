from digital_human.graph.state import AgentState
from digital_human.config.settings import MEMORY_TRIGGERS, MIN_INTENT_CONFIDENCE
from .extractor import extract_memory_intent


def memory_agent(state: AgentState) -> AgentState:
    user_input = state.user_input.lower()

    trigger_found = any(trigger in user_input for trigger in MEMORY_TRIGGERS)
    if not trigger_found:
        return state

    memory_intent = extract_memory_intent(user_input)

    if memory_intent and memory_intent["confidence"] >= MIN_INTENT_CONFIDENCE:
        state.memory_intent = memory_intent
        state.needs_memory = True

    return state
