# import json
# import logging
# from typing import Any, Optional

# from agents import Runner
# from openai.types.responses import ResponseTextDeltaEvent

# # ============================================================
# # SAFE OPTIONAL IMPORT (CRITICAL FIX)
# # ============================================================

# try:
#     from agents.exceptions import GuardrailTripwire
# except ImportError:
#     GuardrailTripwire = None


# from digital_human_sdk.app.intelligence.our_agents.router_agent import router_agent
# from digital_human_sdk.app.intelligence.our_agents.reasoning_agent import reasoning_agent
# from digital_human_sdk.app.intelligence.our_agents.memory_agent import memory_agent
# from digital_human_sdk.app.intelligence.our_agents.tool_agent import tool_agent
# from digital_human_sdk.app.intelligence.tools.tool_executor import ToolExecutor
# from digital_human_sdk.app.intelligence.utils.json_utils import safe_json_loads
# from services.knowledge_base_service import KnowledgeBaseService
# from context.context_builder import ContextBuilder
# from services.memory_service import MemoryService

# # ============================================================
# # LOGGER
# # ============================================================

# logger = logging.getLogger("orchestrator")

# ALLOWED_MEMORY_ACTIONS = {"save", "update", "delete", "none"}

# # ============================================================
# # MAIN ORCHESTRATION ENTRYPOINT
# # ============================================================

# async def run_digital_human_chat(
#     *,
#     llm_messages: list,
#     context: Optional[Any] = None,
# ):
#     """
#     Full orchestration pipeline:
#     Input → Router → Memory → Tools → Reasoning → Streaming
#     """

#     logger.info("🔥 Orchestrator started")

#     # --------------------------------------------------
#     # 0️⃣ USER INPUT
#     # --------------------------------------------------
#     user_input = next(
#         (m.get("content") for m in reversed(llm_messages) if m.get("role") == "user"),
#         "",
#     )
#     router_input = user_input

#     if context and context.db:
#         router_input = ContextBuilder.build_router_context(
#             db=context.db,
#             session_id=context.session_id,
#             user_input=user_input
#         )


#     if not isinstance(user_input, str) or not user_input.strip():
#         yield {"type": "token", "value": "Hi! How can I help you today? 😊"}
#         return

#     # --------------------------------------------------
#     # 1️⃣ ROUTER (INPUT GUARDRAILS APPLY HERE)
#     # --------------------------------------------------
#     router_decision = {
#         "use_tool": False,
#         "use_memory": False,
#         "intent": "none",
#     }

#     try:
#         router_raw = await Runner.run(
#             router_agent,
#             router_input,
#             context=context,
#             max_turns=1,
#         )

#         parsed = safe_json_loads(router_raw.final_output, default={})
#         if isinstance(parsed, dict):
#             router_decision.update(parsed)

#     except Exception as e:
#         # ✅ GuardrailTripwire (ONLY if it exists)
#         if GuardrailTripwire and isinstance(e, GuardrailTripwire):
#             if e.tripwire_triggered:
#                 msg = (
#                     e.output_info.get("message")
#                     if isinstance(e.output_info, dict)
#                     else "Sorry, I can’t help with that request."
#                 )
#                 yield {"type": "token", "value": msg}
#                 return

#         logger.exception("Router failed — continuing without routing")
# # --------------------------------------------------
#     # 2️⃣.5 KNOWLEDGE BASE READ (ADMIN DOCS)
#     # --------------------------------------------------
#     kb_data = []
#     kb_found = False

#     try:
#         kb_data = KnowledgeBaseService.read(
#             query=router_input,
#             limit=5,
#             document_types=["FAQ", "POLICY"],
#             industry="fintech",
#         )
#         kb_found = bool(kb_data)
#     except Exception:
#         logger.exception("Knowledge base read failed")


#     # --------------------------------------------------
#     # 2️⃣ MEMORY READ
#     # --------------------------------------------------
#     memory_data = []

#     if context and getattr(context, "enable_memory", False):
#         try:
#             memory_data = MemoryService.read(
#                 user_id=context.user_id,
#                 query=router_input,
#                 limit=3,
#             )
#         except Exception:
#             logger.exception("Memory read failed")
    
    
#     # --------------------------------------------------
#     # 3️⃣ MEMORY WRITE (EVENT ONLY)
#     # --------------------------------------------------
#     if (
#         router_decision.get("use_memory")
#         and router_decision.get("intent") == "write"
#         and context
#         and getattr(context, "enable_memory", False)
#     ):
#         try:
#             mem_raw = await Runner.run(
#                 memory_agent,
#                 router_input,
#                 context=context,
#                 max_turns=1,
#             )

#             memory_action = safe_json_loads(mem_raw.final_output, default={})
#             if memory_action.get("action") in ALLOWED_MEMORY_ACTIONS:
#                 yield {"type": "memory_event", "payload": memory_action}

#         except Exception:
#             logger.exception("Memory write failed")

#     # --------------------------------------------------
#     # 4️⃣ TOOL EXECUTION
#     # --------------------------------------------------
#     tool_context = {}

#     if router_decision.get("use_tool"):
#         try:
#             tool_raw = await Runner.run(
#                 tool_agent,
#                 router_input,
#                 context=context,
#                 max_turns=1,
#             )

#             tool_payload = safe_json_loads(tool_raw.final_output, default={})

#             tool_context = ToolExecutor.execute(
#                 tool_payload.get("tool"),
#                 tool_payload.get("arguments", {}),
#             )

#             if hasattr(tool_context, "model_dump"):
#                 tool_context = tool_context.model_dump()

#         except Exception:
#             logger.exception("Tool execution failed")
#             tool_context = {"error": "Tool execution failed"}

#     # --------------------------------------------------
#     # 5️⃣ REASONING (OUTPUT GUARDRAILS APPLY HERE)
#     # --------------------------------------------------
#     reasoning_input = {
#         "messages": llm_messages,
#         "memory": memory_data,
#         "tool_context": tool_context,
#                 # admin knowledge base (RAG)
#         "knowledge_base": kb_data,
#         "kb_found": kb_found,
#     }

#     emitted = False

#     try:
#         reasoning_stream = Runner.run_streamed(
#             reasoning_agent,
#             json.dumps(reasoning_input),
#             context=context,
#         )

#         async for event in reasoning_stream.stream_events():
#             if (
#                 event.type == "raw_response_event"
#                 and isinstance(event.data, ResponseTextDeltaEvent)
#             ):
#                 emitted = True
#                 yield {"type": "token", "value": event.data.delta}

#     except Exception as e:
#         if GuardrailTripwire and isinstance(e, GuardrailTripwire):
#             if e.tripwire_triggered:
#                 msg = (
#                     e.output_info.get("message")
#                     if isinstance(e.output_info, dict)
#                     else "I can’t share that information."
#                 )
#                 yield {"type": "token", "value": msg}
#                 yield {"type": "done"}
#                 return
        
#         logger.exception("Reasoning failed")
#         yield {
#             "type": "token",
#             "value": "Something went wrong, but I’m still here. Please try again.",
#         }

#     # --------------------------------------------------
#     # 6️⃣ NEVER SILENT FALLBACK
#     # --------------------------------------------------
#     if not emitted:
#         yield {
#             "type": "token",
#             "value": "I’m here 😊 What would you like to know?",
#         }
import json
import logging
from typing import Any, Optional

from agents import Runner
from openai.types.responses import ResponseTextDeltaEvent

# ============================================================
# SAFE OPTIONAL IMPORT (CRITICAL FIX)
# ============================================================

try:
    from agents.exceptions import GuardrailTripwire
except ImportError:
    GuardrailTripwire = None

# ============================================================
# INTERNAL IMPORTS
# ============================================================

from digital_human_sdk.app.intelligence.our_agents.router_agent import router_agent
from digital_human_sdk.app.intelligence.our_agents.reasoning_agent import reasoning_agent
from digital_human_sdk.app.intelligence.our_agents.memory_agent import memory_agent
from digital_human_sdk.app.intelligence.our_agents.tool_agent import tool_agent
from digital_human_sdk.app.intelligence.tools.tool_executor import ToolExecutor
from digital_human_sdk.app.intelligence.utils.json_utils import safe_json_loads
from services.knowledge_base_service import KnowledgeBaseService
from context.context_builder import ContextBuilder
from services.memory_service import MemoryService

# ============================================================
# LOGGER
# ============================================================

logger = logging.getLogger("orchestrator")

ALLOWED_MEMORY_ACTIONS = {"save", "update", "delete", "none"}

# ============================================================
# MAIN ORCHESTRATION ENTRYPOINT
# ============================================================

async def run_digital_human_chat(
    *,
    llm_messages: list,
    context: Optional[Any] = None,
):
    """
    Full orchestration pipeline:
    Input → Memory Read → KB Read → Router → Memory Write → Tools → Reasoning
    """

    logger.info("🔥 Orchestrator started")

    # --------------------------------------------------
    # 0️⃣ USER INPUT
    # --------------------------------------------------
    user_input = next(
        (m.get("content") for m in reversed(llm_messages) if m.get("role") == "user"),
        "",
    )

    if not isinstance(user_input, str) or not user_input.strip():
        yield {"type": "token", "value": "Hi! How can I help you today? 😊"}
        return

    router_input = user_input

    if context and context.db:
        router_input = ContextBuilder.build_router_context(
            db=context.db,
            session_id=context.session_id,
            user_input=user_input,
        )

    # --------------------------------------------------
    # 1️⃣ MEMORY READ (BEFORE ROUTER ✅)
    # --------------------------------------------------
    memory_data = []

    if context and getattr(context, "enable_memory", False):
        try:
            memory_data = MemoryService.read(
                user_id=context.user_id,
                query=user_input,
                limit=3,
            )
        except Exception:
            logger.exception("Memory read failed")

    # --------------------------------------------------
    # 2️⃣ KNOWLEDGE BASE READ
    # --------------------------------------------------
    kb_data = []
    kb_found = False

    try:
        kb_data = KnowledgeBaseService.read(
            query=router_input,
            limit=5,
            document_types=["FAQ", "POLICY"],
            industry="fintech",
        )
        kb_found = bool(kb_data)
    except Exception:
        logger.exception("Knowledge base read failed")

    # --------------------------------------------------
    # 3️⃣ ROUTER (NOW MEMORY + KB AWARE ✅)
    # --------------------------------------------------
    router_decision = {
        "use_tool": False,
        "use_memory": False,
        "intent": "none",
    }

    try:
        router_payload = {
            "user_input": user_input,
            "existing_memory": memory_data,
            "knowledge_base": kb_data,
        }

        router_raw = await Runner.run(
            router_agent,
            json.dumps(router_payload),
            context=context,
            max_turns=1,
        )

        parsed = safe_json_loads(router_raw.final_output, default={})
        if isinstance(parsed, dict):
            router_decision.update(parsed)

    except Exception as e:
        if GuardrailTripwire and isinstance(e, GuardrailTripwire):
            if e.tripwire_triggered:
                msg = (
                    e.output_info.get("message")
                    if isinstance(e.output_info, dict)
                    else "Sorry, I can’t help with that request."
                )
                yield {"type": "token", "value": msg}
                return

        logger.exception("Router failed — continuing without routing")

    # --------------------------------------------------
    # 4️⃣ MEMORY WRITE (DEDUP SAFE ✅)
    # --------------------------------------------------
    if (
        router_decision.get("use_memory")
        and router_decision.get("intent") == "write"
        and context
        and getattr(context, "enable_memory", False)
    ):
        try:
            mem_raw = await Runner.run(
                memory_agent,
                json.dumps(
                    {
                        "user_input": user_input,
                        "existing_memory": memory_data,
                    }
                ),
                context=context,
                max_turns=1,
            )

            memory_action = safe_json_loads(mem_raw.final_output, default={})

            # HARD DUPLICATE PROTECTION
            existing_contents = {
                m.get("content") for m in memory_data if isinstance(m, dict)
            }

            if (
                memory_action.get("action") in ALLOWED_MEMORY_ACTIONS
                and memory_action.get("content") not in existing_contents
            ):
                yield {"type": "memory_event", "payload": memory_action}
            else:
                logger.info("🧠 Duplicate memory skipped")

        except Exception:
            logger.exception("Memory write failed")

    # --------------------------------------------------
    # 5️⃣ TOOL EXECUTION
    # --------------------------------------------------
    tool_context = {}

    if router_decision.get("use_tool"):
        try:
            tool_raw = await Runner.run(
                tool_agent,
                router_input,
                context=context,
                max_turns=1,
            )

            tool_payload = safe_json_loads(tool_raw.final_output, default={})

            tool_context = ToolExecutor.execute(
                tool_payload.get("tool"),
                tool_payload.get("arguments", {}),
            )

            if hasattr(tool_context, "model_dump"):
                tool_context = tool_context.model_dump()

        except Exception:
            logger.exception("Tool execution failed")
            tool_context = {"error": "Tool execution failed"}

    # --------------------------------------------------
    # 6️⃣ REASONING (OUTPUT GUARDRAILS APPLY)
    # --------------------------------------------------
    reasoning_input = {
        "messages": llm_messages,
        "memory": memory_data,
        "tool_context": tool_context,
        "knowledge_base": kb_data,
        "kb_found": kb_found,
    }

    emitted = False

    try:
        reasoning_stream = Runner.run_streamed(
            reasoning_agent,
            json.dumps(reasoning_input),
            context=context,
        )

        async for event in reasoning_stream.stream_events():
            if (
                event.type == "raw_response_event"
                and isinstance(event.data, ResponseTextDeltaEvent)
            ):
                emitted = True
                yield {"type": "token", "value": event.data.delta}

    except Exception as e:
        if GuardrailTripwire and isinstance(e, GuardrailTripwire):
            if e.tripwire_triggered:
                msg = (
                    e.output_info.get("message")
                    if isinstance(e.output_info, dict)
                    else "I can’t share that information."
                )
                yield {"type": "token", "value": msg}
                yield {"type": "done"}
                return

        logger.exception("Reasoning failed")
        yield {
            "type": "token",
            "value": "Something went wrong, but I’m still here. Please try again.",
        }

    # --------------------------------------------------
    # 7️⃣ NEVER SILENT FALLBACK
    # --------------------------------------------------
    if not emitted:
        yield {"type": "token", "value": "I’m here 😊 What would you like to know?"}
