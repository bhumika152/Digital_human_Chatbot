# import json
# import logging
# from typing import Any, Optional

# from agents import Runner
# from openai.types.responses import ResponseTextDeltaEvent

# from digital_human_sdk.app.intelligence.safety.safety_agent import safe_agent
# from digital_human_sdk.app.intelligence.our_agents.router_agent import router_agent
# from digital_human_sdk.app.intelligence.our_agents.memory_agent import memory_agent
# from digital_human_sdk.app.intelligence.our_agents.tool_agent import tool_agent
# from digital_human_sdk.app.intelligence.our_agents.reasoning_agent import reasoning_agent
# from digital_human_sdk.app.intelligence.tools.tool_executor import ToolExecutor
# from digital_human_sdk.app.intelligence.utils.json_utils import safe_json_loads

# try:
#     from agents.exceptions import GuardrailTripwire
# except ImportError:
#     GuardrailTripwire = None


# logger = logging.getLogger("orchestrator")

# ALLOWED_MEMORY_ACTIONS = {"save", "update", "delete", "none"}

# # --------------------------------------------------
# # CORE CHAT ORCHESTRATOR
# # --------------------------------------------------
# async def run_digital_human_chat(
#     *,
#     llm_messages: list,
#     context: Optional[Any] = None,
# ):
#     enable_memory = bool(getattr(context, "enable_memory", False))
#     enable_tools = bool(getattr(context, "enable_tools", False))
#     enable_rag = bool(getattr(context, "enable_rag", False))

#     # --------------------------------------------------
#     # 1️⃣ USER INPUT
#     # --------------------------------------------------
#     logger.info("🔥 LOG TEST: orchestrator started")

#     user_input = next(
#         msg["content"]
#         for msg in reversed(llm_messages)
#         if msg["role"] == "user"
#     )

#     router_input = user_input

#     if getattr(context, "router_context", None):
#         router_input = f"""
# Conversation context:
# {context.router_context}

# User message:
# {user_input}
# """.strip()

#     logger.info("🧑 USER_INPUT | %s", user_input)
#     logger.info(
#         "🧩 CONTEXT | user_id=%s | enable_memory=%s",
#         getattr(context, "user_id", None),
#         enable_memory,
#     )

#     # --------------------------------------------------
#     # 2️⃣ MEMORY READ
#     # --------------------------------------------------
#     memory_data = []
#     memory_found = False

#     if enable_memory:
#         logger.info("📥 Fetching semantic memory")
#         memory_data = getattr(context, "memory_data", [])
#         memory_found = bool(memory_data)

#     logger.info(
#         "🧠 MEMORY_RESULT | found=%s | count=%d",
#         memory_found,
#         len(memory_data),
#     )

#     # --------------------------------------------------
#     # 3️⃣ KNOWLEDGE BASE READ
#     # --------------------------------------------------
#     kb_data = []
#     kb_found = False

#     if enable_rag:
#         logger.info("📚 Fetching knowledge base")
#         kb_data = getattr(context, "kb_data", [])
#         kb_found = bool(kb_data)

#     logger.info(
#         "📚 KB_RESULT | found=%s | count=%d",
#         kb_found,
#         len(kb_data),
#     )

#     # --------------------------------------------------
#     # 4️⃣ ROUTER
#     # --------------------------------------------------
#     router_decision = {
#         "use_tool": False,
#         "use_memory": False,
#         "intent": "none",
#     }

#     try:
#         router_payload = {
#             "user_input": user_input,
#             "existing_memory": memory_data,
#             "knowledge_base": kb_data,
#         }

#         logger.info("🧭 Running router agent")

#         router_raw = await Runner.run(
#             router_agent,
#             json.dumps(router_payload),
#             context=context,
#             max_turns=1,
#         )

#         parsed = safe_json_loads(router_raw.final_output, default={})
#         logger.info("🧭 Router output: %s", parsed)

#         if isinstance(parsed, dict):
#             router_decision.update(parsed)

#     except Exception as e:
#         if GuardrailTripwire and isinstance(e, GuardrailTripwire) and e.tripwire_triggered:
#             logger.warning("🚫 Router guardrail triggered")
#             yield {"type": "token", "value": "Sorry, I can’t help with that request."}
#             return

#         logger.exception("❌ Router failed")

#     # --------------------------------------------------
#     # 5️⃣ MEMORY WRITE
#     # --------------------------------------------------
#     if (
#         router_decision.get("use_memory")
#         and router_decision.get("intent") == "write"
#         and enable_memory
#     ):
#         try:
#             mem_raw = await Runner.run(
#                 memory_agent,
#                 json.dumps(
#                     {
#                         "user_input": user_input,
#                         "existing_memory": memory_data,
#                     }
#                 ),
#                 context=context,
#                 max_turns=1,
#             )

#             memory_action = safe_json_loads(mem_raw.final_output, default={})
#             action_type = memory_action.get("action")

#             logger.info("🧠 Memory action: %s", memory_action)

#             if action_type in ALLOWED_MEMORY_ACTIONS:
#                 yield {"type": "memory_event", "payload": memory_action}

#         except Exception:
#             logger.exception("❌ Memory write failed")

#     # # --------------------------------------------------
#     # # 6️⃣ TOOL EXECUTION (GENERIC)
#     # # --------------------------------------------------
#     # tool_context = {}

#     # if router_decision.get("use_tool"):
#     #     try:
#     #         logger.info("🛠️ Tool execution started")

#     #         tool_raw = await Runner.run(
#     #             tool_agent,
#     #             router_input,
#     #             context=context,
#     #             max_turns=1,
#     #         )

#     #         tool_payload = safe_json_loads(tool_raw.final_output, default={})
#     #         logger.info("🛠️ Tool payload: %s", tool_payload)

#     #         tool_name = tool_payload.get("tool")
#     #         tool_arguments = tool_payload.get("arguments", {})

#     #         # 🔐 JWT injection (generic)
#     #         if context and hasattr(context, "auth_token"):
#     #             tool_arguments["auth_token"] = context.auth_token

#     #         tool_context = ToolExecutor.execute(
#     #             tool_name,
#     #             tool_arguments,
#     #         )

#     #         if hasattr(tool_context, "model_dump"):
#     #             tool_context = tool_context.model_dump()

#     #         logger.info("🛠️ Tool response: %s", tool_context)

#     #     except Exception:
#     #         logger.exception("❌ Tool execution failed")
#         #         tool_context = {"error": "Tool execution failed"}
#     # --------------------------------------------------
#     # 6️⃣ TOOL EXECUTION (SMART PROPERTY FLOW)
#     # --------------------------------------------------
#     tool_context = {}

#     if router_decision.get("use_tool"):
#         try:
#             logger.info("🛠️ Tool execution started")

#             tool_raw = await Runner.run(
#                 tool_agent,
#                 router_input,
#                 context=context,
#                 max_turns=1,
#             )

#             tool_payload = safe_json_loads(tool_raw.final_output, default={})
#             logger.info("🛠️ Tool payload: %s", tool_payload)

#             tool_name = tool_payload.get("tool")
#             tool_arguments = tool_payload.get("arguments", {})

#             # 🔐 JWT injection
#             if context and hasattr(context, "auth_token"):
#                 tool_arguments["auth_token"] = context.auth_token

#             # 🏠 PROPERTY ADD FLOW (INTERCEPT)
#             if tool_name == "property" and tool_arguments.get("action") == "add":
#                 handled = handle_property_add_flow(
#                     context=context,
#                     tool_arguments=tool_arguments,
                    
#                 )
#                 if handled:
#                     yield handled
#                     return

#             # 🔁 Normal tool execution
#             tool_context = ToolExecutor.execute(
#                 tool_name,
#                 tool_arguments,
#             )

#             if hasattr(tool_context, "model_dump"):
#                 tool_context = tool_context.model_dump()

#             logger.info("🛠️ Tool response: %s", tool_context)

#         except Exception:
#             logger.exception("❌ Tool execution failed")
#             tool_context = {"error": "Tool execution failed"}

#     # --------------------------------------------------
#     # 7️⃣ REASONING
#     # --------------------------------------------------
#     reasoning_input = {
#         "messages": llm_messages,
#         "memory": memory_data,
#         "tool_context": tool_context,
#         "knowledge_base": kb_data,
#         "kb_found": kb_found,
#     }

#     emitted = False

#     try:
#         logger.info("🧠 Reasoning started")

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
#         if GuardrailTripwire and isinstance(e, GuardrailTripwire) and e.tripwire_triggered:
#             logger.warning("🚫 Reasoning guardrail triggered")
#             yield {"type": "token", "value": "I can’t share that information."}
#             return

#         logger.exception("❌ Reasoning failed")
#         yield {"type": "token", "value": "Something went wrong. Please try again."}

#     # --------------------------------------------------
#     # 8️⃣ FALLBACK
#     # --------------------------------------------------
#     if not emitted:
#         logger.warning("⚠️ No tokens emitted")
#         yield {"type": "token", "value": "I’m here 😊 What would you like to do next?"}

#     logger.info("✅ Orchestrator completed")
import json
import logging
from typing import Any, Optional
 
from agents import Runner
from openai.types.responses import ResponseTextDeltaEvent
 
from app.intelligence.safety.safety_agent import safe_agent
from app.intelligence.our_agents.router_agent import router_agent
from app.intelligence.our_agents.memory_agent import memory_agent
from app.intelligence.our_agents.tool_agent import tool_agent
from app.intelligence.our_agents.reasoning_agent import reasoning_agent
from app.intelligence.tools.tool_executor import ToolExecutor
from app.intelligence.utils.json_utils import safe_json_loads
 
try:
    from agents.exceptions import GuardrailTripwire
except ImportError:
    GuardrailTripwire = None
 
 
logger = logging.getLogger("orchestrator")
 
ALLOWED_MEMORY_ACTIONS = {"save", "update", "delete", "none"}
 
# --------------------------------------------------
# CORE CHAT ORCHESTRATOR
# --------------------------------------------------
async def run_digital_human_chat(
    *,
    llm_messages: list,
    context: Optional[Any] = None,
):
    enable_memory = bool(getattr(context, "enable_memory", False))
    enable_tools = bool(getattr(context, "enable_tools", False))
    enable_rag = bool(getattr(context, "enable_rag", False))
 
    # --------------------------------------------------
    # 1️⃣ USER INPUT
    # --------------------------------------------------
    logger.info("🔥 LOG TEST: orchestrator started")
 
    user_input = next(
        msg["content"]
        for msg in reversed(llm_messages)
        if msg["role"] == "user"
    )
 
    router_input = user_input
 
    if getattr(context, "router_context", None):
        router_input = f"""
Conversation context:
{context.router_context}
 
User message:
{user_input}
""".strip()
 
    logger.info("🧑 USER_INPUT | %s", user_input)
    logger.info(
        "🧩 CONTEXT | user_id=%s | enable_memory=%s",
        getattr(context, "user_id", None),
        enable_memory,
    )
 
    # --------------------------------------------------
    # 2️⃣ MEMORY READ
    # --------------------------------------------------
    memory_data = []
    memory_found = False
 
    if enable_memory:
        logger.info("📥 Fetching semantic memory")
        memory_data = getattr(context, "memory_data", [])
        memory_found = bool(memory_data)
 
    logger.info(
        "🧠 MEMORY_RESULT | found=%s | count=%d",
        memory_found,
        len(memory_data),
    )
 
    # --------------------------------------------------
    # 3️⃣ KNOWLEDGE BASE READ
    # --------------------------------------------------
    kb_data = []
    kb_found = False
 
    if enable_rag:
        logger.info("📚 Fetching knowledge base")
        kb_data = getattr(context, "kb_data", [])
        kb_found = bool(kb_data)
 
    logger.info(
        "📚 KB_RESULT | found=%s | count=%d",
        kb_found,
        len(kb_data),
    )
 
    # --------------------------------------------------
    # 4️⃣ ROUTER
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
 
        logger.info("🧭 Running router agent")
 
        router_raw = await Runner.run(
            router_agent,
            json.dumps(router_payload),
            context=context,
            max_turns=1,
        )
 
        parsed = safe_json_loads(router_raw.final_output, default={})
        logger.info("🧭 Router output: %s", parsed)
 
        if isinstance(parsed, dict):
            router_decision.update(parsed)
 
    except Exception as e:
        if GuardrailTripwire and isinstance(e, GuardrailTripwire) and e.tripwire_triggered:
            logger.warning("🚫 Router guardrail triggered")
            yield {"type": "token", "value": "Sorry, I can’t help with that request."}
            return
 
        logger.exception("❌ Router failed")
 
    # --------------------------------------------------
    # 5️⃣ MEMORY WRITE
    # --------------------------------------------------
    if (
        router_decision.get("use_memory")
        and router_decision.get("intent") == "write"
        and enable_memory
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
            action_type = memory_action.get("action")
 
            logger.info("🧠 Memory action: %s", memory_action)
 
            if action_type in ALLOWED_MEMORY_ACTIONS:
                yield {"type": "memory_event", "payload": memory_action}
 
        except Exception:
            logger.exception("❌ Memory write failed")
 
    # --------------------------------------------------
    # 6️⃣ TOOL EXECUTION
    # --------------------------------------------------
    tool_context = {}
 
    if router_decision.get("use_tool"):
        try:
            logger.info("🛠️ Tool execution started")
 
            tool_raw = await Runner.run(
                tool_agent,
                router_input,
                context=context,
                max_turns=1,
            )
 
            tool_payload = safe_json_loads(tool_raw.final_output, default={})
            logger.info("🛠️ Tool payload: %s", tool_payload)
 
            tool_name = tool_payload.get("tool")
            tool_arguments = tool_payload.get("arguments", {})
 
            if context and hasattr(context, "auth_token"):
                tool_arguments["auth_token"] = context.auth_token
 
            tool_context = ToolExecutor.execute(
                tool_name,
                tool_arguments,
            )
 
            if hasattr(tool_context, "model_dump"):
                tool_context = tool_context.model_dump()
 
            logger.info("🛠️ Tool response: %s", tool_context)
 
        except Exception:
            logger.exception("❌ Tool execution failed")
            tool_context = {"error": "Tool execution failed"}
 
    # --------------------------------------------------
    # 7️⃣ REASONING
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
        logger.info("🧠 Reasoning started")
        logger.info("🧠 Reasoning input: %s", reasoning_input)
 
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
        if GuardrailTripwire and isinstance(e, GuardrailTripwire) and e.tripwire_triggered:
            logger.warning("🚫 Reasoning guardrail triggered")
            yield {"type": "token", "value": "I can’t share that information."}
            return
 
        logger.exception("❌ Reasoning failed")
        yield {"type": "token", "value": "Something went wrong. Please try again."}
 
    # --------------------------------------------------
    # 8️⃣ FALLBACK
    # --------------------------------------------------
    if not emitted:
        logger.warning("⚠️ No tokens emitted")
        yield {"type": "token", "value": "I’m here 😊 What would you like to do next?"}
 
    logger.info("✅ Orchestrator completed")