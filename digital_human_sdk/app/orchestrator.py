
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
from app.intelligence.tools.property_contract import PROPERTY_ACTION_CONTRACT
from app.intelligence.tools.tool_executor import ToolExecutor
from app.intelligence.utils.json_utils import safe_json_loads
from app.intelligence.tools.property_contract import get_missing_fields

try:
    from agents.exceptions import GuardrailTripwire
except ImportError:
    GuardrailTripwire = None


logger = logging.getLogger("orchestrator")

ALLOWED_MEMORY_ACTIONS = {"save", "update", "delete"}

PROPERTY_UPDATE_SCHEMA = {
    "required": ["property_id"],
    "optional": [
        "title",
        "city",
        "locality",
        "purpose",
        "price",
        "bhk",
        "area_sqft",
        "is_legal",
        "owner_name",
        "contact_phone",
    ]
}

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
            "user_input": router_input,
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
        if (
            GuardrailTripwire
            and isinstance(e, GuardrailTripwire)
            and e.tripwire_triggered
        ):
            logger.warning("🚫 Router guardrail triggered")
            yield {
                "type": "token",
                "value": "Sorry, I can’t help with that request.",
            }
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
            logger.info("🧠 Memory Agent called")
            mem_raw = await Runner.run(
                memory_agent,
                router_input,
                context=context,
                max_turns=1,
            )
            logger.info("🧠 Memory output: %s", mem_raw)

            memory_action = safe_json_loads(mem_raw.final_output, default={})
            action_type = memory_action.get("action")

            logger.info("🧠 Memory action: %s", memory_action)

            if action_type in ALLOWED_MEMORY_ACTIONS:
                yield {
                    "type": "memory_event",
                    "payload": memory_action,
                }

        except Exception:
            logger.exception("❌ Memory write failed")

    # --------------------------------------------------
    # 🧠 MEMORY-AWARE TOOL INPUT ENRICHMENT
    # --------------------------------------------------
    augmented_tool_input = router_input

    if memory_data:
        memory_text = "\n".join(
            f"- {m.get('text')}"
            for m in memory_data
            if isinstance(m, dict) and m.get("text")
        )

        augmented_tool_input = f"""
    User known preferences / memory:
    {memory_text}

    User request:
    {user_input}
    """.strip()

    logger.info("🧠 Tool input enriched with memory")

    # --------------------------------------------------
    # 6️⃣ TOOL EXECUTION (SEARCH + ADD, CONVERSATION BASED)
    # --------------------------------------------------

    tool_context = {}

    # Init contexts once
    if not hasattr(context, "search_context"):
        context.search_context = {}

    if not hasattr(context, "pending_payload"):
        context.pending_payload = {}

    if not hasattr(context, "update_context"):
        context.update_context = {}

    if not hasattr(context, "active_update"):
        context.active_update = False

    if not hasattr(context, "delete_context"):
        context.delete_context = {}

    if not hasattr(context, "active_delete"):
        context.active_delete = False

    if router_decision.get("use_tool"):
        try:
            logger.info("🛠️ Tool execution started")

            # -----------------------------------
            # 6.1 Run tool agent (LLM → tool JSON)
            # -----------------------------------
            if context.active_update or context.active_delete:
                logger.info("🔒 Skipping tool-agent (update in progress)")
                tool_name = "property"
                action = "update"
                tool_arguments = {"action": "update"}
                payload = {}
            else:
                tool_raw = await Runner.run(
                    tool_agent,
                    augmented_tool_input,
                    context=context,
                    max_turns=1,
                )

                tool_payload = safe_json_loads(tool_raw.final_output, default={})
                logger.info("🛠️ Tool payload: %s", tool_payload)

                tool_name = tool_payload.get("tool")
                tool_arguments = tool_payload.get("arguments", {})
                action = tool_arguments.get("action")
                payload = tool_arguments.get("payload", {})

            # -----------------------------------
            # 6.2 AUTH TOKEN
            # -----------------------------------
            if getattr(context, "auth_token", None):
                tool_arguments["auth_token"] = context.auth_token

            # ==================================================
            # 🔍 SEARCH FLOW (conversation-based)
            # ==================================================
            if tool_name == "property" and action == "search":

                # Merge fields across turns
                context.search_context.update(payload)

                effective_payload = {
                    "city": context.search_context.get("city"),
                    "purpose": context.search_context.get("purpose"),
                    "budget": context.search_context.get("budget"),
                }

                tool_arguments["payload"] = effective_payload

                missing_fields = get_missing_fields(
                    PROPERTY_ACTION_CONTRACT,
                    "search",
                    effective_payload,
                )

                if missing_fields:
                    ask_message = PROPERTY_ACTION_CONTRACT["search"]["ask_message"]
                    yield {
                        "type": "token",
                        "value": f"{ask_message} {', '.join(missing_fields)}.",
                    }
                    return  # ⛔ Wait for user input

                # Execute search immediately when complete
                tool_context = ToolExecutor.execute(
                    tool_name,
                    tool_arguments,
                )

                if hasattr(tool_context, "model_dump"):
                    tool_context = tool_context.model_dump()

                logger.info("🛠️ Search response: %s", tool_context)

                # Reset search context after successful search
                context.search_context = {}

            # ==================================================
            # ➕ ADD FLOW (conversation-based, stateful)
            # ==================================================
            elif tool_name == "property" and action == "add":

                # Merge payload across turns
                payload = {**context.pending_payload, **payload}
                tool_arguments["payload"] = payload

                missing_fields = get_missing_fields(
                    PROPERTY_ACTION_CONTRACT,
                    "add",
                    payload,
                )

                if missing_fields:
                    context.pending_payload = payload
                    context.pending_tool = "property.add"

                    ask_message = PROPERTY_ACTION_CONTRACT["add"]["ask_message"]
                    yield {
                        "type": "token",
                        "value": f"{ask_message} {', '.join(missing_fields)}.",
                    }
                    return  # ⛔ Wait for user input

                # Execute add immediately when complete
                tool_context = ToolExecutor.execute(
                    tool_name,
                    tool_arguments,
                )

                if hasattr(tool_context, "model_dump"):
                    tool_context = tool_context.model_dump()

                logger.info("🛠️ Add response: %s", tool_context)

                # Clear add state after success
                context.pending_payload = {}
                context.pending_tool = None
            
            # ==================================================
            # UPDATE FLOW
            # ==================================================
            elif tool_name == "property" and action == "update":

                context.active_update = True

                # 🔥 Recover property_id if LLM dropped it
                if "property_id" not in tool_arguments:
                    import re
                    match = re.search(r"\bproperty[_ ]?id\s*(\d+)", user_input, re.I)
                    if match:
                        tool_arguments["property_id"] = int(match.group(1))

                # Normalize id alias
                if "id" in tool_arguments and "property_id" not in tool_arguments:
                    tool_arguments["property_id"] = tool_arguments.pop("id")

                # Persist property_id
                if tool_arguments.get("property_id"):
                    context.update_context["property_id"] = tool_arguments["property_id"]

                # Move update fields into payload
                for field in PROPERTY_UPDATE_SCHEMA["optional"]:
                    if field in tool_arguments:
                        payload[field] = tool_arguments[field]

                context.update_context.update(payload)

                missing_fields = get_missing_fields(
                    PROPERTY_ACTION_CONTRACT,
                    "update",
                    context.update_context,
                )

                if missing_fields:
                    yield {
                        "type": "token",
                        "value": PROPERTY_ACTION_CONTRACT["update"]["ask_message"],
                    }
                    return

                property_id = context.update_context.pop("property_id")

                tool_context = ToolExecutor.execute(
                    tool_name,
                    {
                        "action": "update",
                        "property_id": property_id,
                        "payload": context.update_context,
                        "auth_token": context.auth_token,
                    },
                )

                context.update_context = {}
                context.active_update = False

            # ==================================================
            # ❌ DELETE FLOW (conversation-based, stateful)
            # ==================================================
            elif tool_name == "property" and action == "delete":

                context.active_delete = True

                # Normalize id alias
                if "id" in tool_arguments and "property_id" not in tool_arguments:
                    tool_arguments["property_id"] = tool_arguments.pop("id")

                # Recover from text if LLM missed it
                if "property_id" not in tool_arguments:
                    import re
                    match = re.search(r"\b(\d+)\b", user_input)
                    if match:
                        tool_arguments["property_id"] = int(match.group(1))

                # Persist property_id
                if tool_arguments.get("property_id"):
                    context.delete_context["property_id"] = tool_arguments["property_id"]

                # Check missing field
                if "property_id" not in context.delete_context:
                    yield {
                        "type": "token",
                        "value": "Please tell me the property_id you want to delete.",
                    }
                    return

                property_id = context.delete_context["property_id"]

                # 🔥 EXECUTE DELETE WITH AUTH
                tool_context = ToolExecutor.execute(
                    "property",
                    {
                        "action": "delete",
                        "property_id": property_id,
                        "auth_token": context.auth_token,
                    },
                )

                # Reset delete state
                context.delete_context = {}
                context.active_delete = False


            # ==================================================
            # 🚫 OTHER TOOLS (fallback)
            # ==================================================
            else:
                tool_context = ToolExecutor.execute(
                    tool_name,
                    tool_arguments,
                )

                if hasattr(tool_context, "model_dump"):
                    tool_context = tool_context.model_dump()
                
                logger.info("✅ Tool executed successfully: %s", tool_context)


        except Exception:
            logger.exception("❌ Tool execution failed")
            tool_context = {"error": "Tool execution failed"}

   
    # --------------------------------------------------
    # 7️⃣ FINAL REASONING (FIXED)
    # --------------------------------------------------
    final_messages = []

    # Inject memory as SYSTEM text
    if memory_data:
        final_messages.append({
            "role": "system",
            "content": "Known user facts:\n"
                       + "\n".join(f"- {m.get('text')}" for m in memory_data)
        })

    # Inject tool output as SYSTEM text
    if tool_context:
        final_messages.append({
            "role": "system",
            "content": f"Tool result:\n{tool_context}"
        })

    if kb_data:
        final_messages.append({
            "role": "system",
            "content": "Relevant knowledge base information:\n\n" +
                    "\n\n".join(
                        f"- {chunk.get('content')}"
                        for chunk in kb_data
                        if isinstance(chunk, dict) and chunk.get("content")
                    )
        })

    # Add conversation messages directly (NO JSON)
    final_messages.extend(llm_messages)

    # Safety check (must never fail)
    for m in final_messages:
        assert not m["content"].strip().startswith("{\"messages\""), \
            "❌ JSON payload leaked into LLM messages"

    logger.info(
        "🧠 FINAL_REASONING_MESSAGES = %d",
        len(final_messages)
    )

    emitted = False

    try:
        logger.info("🧠 Running reasoning agent")
        reasoning_stream = Runner.run_streamed(
            reasoning_agent,
            final_messages,     
            context=context,
        )

        async for event in reasoning_stream.stream_events():
            if (
                event.type == "raw_response_event"
                and isinstance(event.data, ResponseTextDeltaEvent)
            ):
                emitted = True
                yield {
                    "type": "token",
                    "value": event.data.delta,
                }

    except Exception as e:
        if (
            GuardrailTripwire
            and isinstance(e, GuardrailTripwire)
            and e.tripwire_triggered
        ):
            logger.warning("🚫 Reasoning guardrail triggered")
            yield {
                "type": "token",
                "value": "I can’t share that information.",
            }
            return

        logger.exception("❌ Reasoning failed")
        yield {
            "type": "token",
            "value": "Something went wrong. Please try again.",
        }

    # --------------------------------------------------
    # 8️⃣ FALLBACK
    # --------------------------------------------------
    if not emitted:
        logger.warning("⚠️ No tokens emitted")
        yield {
            "type": "token",
            "value": "I’m here 😊 What would you like to do next?",
        }

    logger.info("✅ Orchestrator completed")
