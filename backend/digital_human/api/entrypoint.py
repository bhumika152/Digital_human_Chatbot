# digital_human/api/entrypoint.py

from graph.state import AgentState, Message
from api.models import TeamARequest, TeamBResponse


def map_team_a_to_state(req: TeamARequest) -> AgentState:
    """
    Converts Team A payload into internal AgentState.
    """
    return AgentState(
        request_id=req.request_id,
        user_input=req.message.content,
        chat_history=[
            Message(**msg) for msg in req.context.recent_messages
        ],
        token_budget=req.system_constraints.token_budget
    )


def map_state_to_team_b_response(state: AgentState) -> TeamBResponse:
    """
    Converts final AgentState into Team B API response.
    """
    return TeamBResponse(
        request_id=state.request_id,
        final_response=state.final_response or "",
        memory_intents=[state.memory_intent] if state.memory_intent else [],
        tool_intents=[state.tool_intent] if state.tool_intent else []
    )
