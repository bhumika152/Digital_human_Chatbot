# from agents import function_tool, RunContextWrapper
# from backend.context.agent_context import AgentRunContext

# @function_tool
# def get_user_info(ctx: RunContextWrapper[AgentRunContext]) -> dict:
#     """
#     Tool that safely accesses backend-only user info
#     """
#     return {
#         "user_id": ctx.context.user_id,
#         "session_id": ctx.context.session_id
#     }
