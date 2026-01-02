import uuid
from digital_human.graph.state import AgentState
from digital_human.graph.graph import run_digital_human
from digital_human.agents.responder_agent.agent import responder_stream


def run_digital_human_chat(
    user_input: str,
    chat_history: list | None = None,
    token_budget: int = 4000,
):
    if chat_history is None:
        chat_history = []

    state = AgentState(
        request_id=str(uuid.uuid4()),
        user_input=user_input,
        chat_history=chat_history,
        token_budget=token_budget,
    )

    # Run LangGraph
    run_digital_human(state)

    # Collect streamed response
    response_text = ""
    for token in responder_stream(state):
        response_text += token

    return {
        "response": response_text,
        "memory_intent": state.memory_intent,
        "rag_used": getattr(state, "rag_used", False),
    }
