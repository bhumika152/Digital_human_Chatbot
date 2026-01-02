from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class AgentState(BaseModel):
    # --------------------------------------------------
    # Request / Session
    # --------------------------------------------------
    request_id: str
    user_input: str
    chat_history: List[Dict[str, str]]
    token_budget: int

    # --------------------------------------------------
    # Orchestrator routing flags (MUST be bool, not Optional)
    # --------------------------------------------------
    needs_reasoning: bool = True
    needs_memory: bool = False
    needs_tools: bool = False

    # --------------------------------------------------
    # Reasoning Agent output
    # --------------------------------------------------
    intent: Optional[Dict[str, Any]] = None
    intent_confidence: Optional[float] = None

    # --------------------------------------------------
    # Memory Agent output
    # --------------------------------------------------
    memory_intent: Optional[Dict[str, Any]] = None
    retrieved_memories: Optional[List[Dict[str, Any]]] = None

    # --------------------------------------------------
    # Tool planning & execution
    # --------------------------------------------------
    tool_request: Optional[Dict[str, Any]] = None
    tool_results: Optional[Dict[str, Any]] = None

    # --------------------------------------------------
    # Final response
    # --------------------------------------------------
    final_response: Optional[str] = None

    # --------------------------------------------------
    # Analytics / integration flags
    # --------------------------------------------------
    used_tools: bool = False
    used_memory: bool = False
