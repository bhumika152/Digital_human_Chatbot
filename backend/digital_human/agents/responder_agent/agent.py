from typing import List, Dict
from digital_human.graph.state import AgentState
from digital_human.llm.openai_client import client
from digital_human.agents.responder_agent.prompts import SYSTEM_PROMPT


# --------------------------------------------------
# Helper: build messages for LLM
# --------------------------------------------------
def build_messages(state: AgentState) -> List[Dict[str, str]]:
    """
    Build OpenAI messages from AgentState.
    This is shared by streaming and non-streaming responders.
    """

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    #  Intent grounding
    if getattr(state, "intent", None):
        messages.append({
            "role": "system",
            "content": f"User intent: {state.intent}"
        })

    #  Memory grounding (if recall is added later)
    if getattr(state, "retrieved_memories", None):
        messages.append({
            "role": "system",
            "content": f"Relevant user memories: {state.retrieved_memories}"
        })

    #  Tool grounding
    if getattr(state, "tool_results", None):
        messages.append({
            "role": "system",
            "content": (
                "Use ONLY the following external information to answer:\n"
                f"{state.tool_results}"
            )
        })

    # User message (last)
    messages.append({
        "role": "user",
        "content": state.user_input
    })

    return messages


# --------------------------------------------------
# LangGraph Responder Node (NON-STREAMING)
# --------------------------------------------------
def responder_node(state: AgentState) -> AgentState:
    """
    LangGraph-safe responder node.

    Rules:
    - MUST return AgentState
    - MUST NOT stream
    - MUST NOT yield
    """

    messages = build_messages(state)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.4
    )

    state.final_response = response.choices[0].message.content

    # Flags for backend / frontend analytics
    state.used_tools = bool(getattr(state, "tool_results", None))
    state.used_memory = bool(getattr(state, "memory_intent", None))

    return state


# --------------------------------------------------
# Streaming Responder (OUTSIDE LangGraph)
# --------------------------------------------------
def responder_stream(state: AgentState):
    """
    Streaming responder.

    IMPORTANT:
    - NOT a LangGraph node
    - MUST NOT be added to the graph
    - Used only by CLI / Backend / SSE / WebSocket
    """

    messages = build_messages(state)

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.4,
        stream=True
    )

    full_response = ""

    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            token = delta.content
            full_response += token
            yield token  

    # Save final response back into state
    state.final_response = full_response
