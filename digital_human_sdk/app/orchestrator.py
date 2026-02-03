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


REQUIRED_PROPERTY_FIELDS = [
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

PROPERTY_FIELD_ALIASES = {
    "title": ["title", "name"],
    "city": ["city"],
    "locality": ["locality", "region", "location"],
    "purpose": ["purpose"],
    "price": ["price", "budget"],
    "bhk": ["bhk", "configuration"],
    "area_sqft": ["area_sqft", "area", "sqt"],
    "is_legal": ["is_legal", "availability", "is_rented"],
    "owner_name": ["owner_name", "contact_person"],
    "contact_phone": ["contact_phone", "owner_contact", "contact_number"],
}

def normalize_property_payload(data: dict) -> dict:
    normalized = {}

    for canonical, aliases in PROPERTY_FIELD_ALIASES.items():
        for alias in aliases:
            if alias in data and data[alias] not in (None, ""):
                value = data[alias]

                # conversions
                if canonical == "bhk" and isinstance(value, str):
                    value = int("".join(filter(str.isdigit, value)))

                if canonical == "area_sqft" and isinstance(value, str):
                    value = int("".join(filter(str.isdigit, value)))

                if canonical == "is_legal":
                    value = bool(value)

                normalized[canonical] = value
                break

    return normalized


def get_missing_fields(payload: dict, required: list) -> list:
    missing = []
    for field in required:
        if field not in payload:
            missing.append(field)
            continue

        val = payload[field]

        if isinstance(val, str) and not val.strip():
            missing.append(field)
        elif field in {"price", "bhk", "area_sqft"} and val <= 0:
            missing.append(field)
        elif field == "is_legal" and not isinstance(val, bool):
            missing.append(field)

    return missing


def extract_property_fields(text: str) -> dict:
    text_l = text.lower()
    data = {}

    # BHK
    if "bhk" in text_l:
        data["bhk"] = int("".join(filter(str.isdigit, text_l)))

    # Area
    if "sqft" in text_l or "sqt" in text_l:
        data["area_sqft"] = int("".join(filter(str.isdigit, text_l)))

    # Price
    if "rs" in text_l or "₹" in text_l:
        data["price"] = int("".join(filter(str.isdigit, text_l)))

    # Legal
    if "true" in text_l or "false" in text_l:
        data["is_legal"] = "true" in text_l

    # Title (fallback)
    if "property" in text_l:
        data["title"] = "Rental Property"

    return data

# --------------------------------------------------
# CORE CHAT ORCHESTRATOR
# --------------------------------------------------
async def run_digital_human_chat(
    *,
    llm_messages: list,
    context: Optional[Any] = None,
):
    if context:
        if not hasattr(context, "pending_action"):
            context.pending_action = None
        if not hasattr(context, "partial_payload"):
            context.partial_payload = {}

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

    if context and getattr(context, "pending_action", None) == "add_property":
        incoming = normalize_property_payload(router_args or {})
        incoming.update(normalize_property_payload(extract_property_fields(user_input)))

        for k, v in incoming.items():
            if k not in context.partial_payload:
                context.partial_payload[k] = v

    router_input = user_input

    if getattr(context, "router_context", None):
        router_input = f"""
    Conversation context:
    {context.router_context}

    User message:
    {user_input}
    """.strip()


    if context and getattr(context, "db", None):
        router_input = ContextBuilder.build_router_context(
            db=context.db,
            session_id=context.session_id,
            user_input=user_input
        )


    logger.info("🧑 USER_INPUT | %s", user_input)
    logger.info(
        "🧩 CONTEXT | user_id=%s | enable_memory=%s | db=%s",
        getattr(context, "user_id", None),
        getattr(context, "enable_memory", None),
        getattr(context, "db", None),
    )

    # --------------------------------------------------
    # 3️⃣ MEMORY READ
    # --------------------------------------------------
    memory_data = []
    memory_found = False

    if context and context.enable_memory:
        logger.info("📥 Fetching semantic memory (via MemoryService)")

        memory_data = getattr(context, "memory_data", [])
        memory_found = len(memory_data) > 0


    logger.info(
        "🧠 MEMORY_RESULT | found=%s | count=%d",
        memory_found,
        len(memory_data),
    )
    # --------------------------------------------------
    # 5️⃣ KNOWLEDGE BASE READ (SAME AS MEMORY)
    # --------------------------------------------------
    kb_data = []
    kb_found = False

    if context and context.enable_rag:
        logger.info("📚 Fetching knowledge base (via context)")
        kb_data = getattr(context, "kb_data", [])
        kb_found = bool(kb_data)

    logger.info(
        "📚 KB_RESULT | found=%s | count=%d",
        kb_found,
        len(kb_data),
    )

     
    # --------------------------------------------------
    # 3️⃣ ROUTER
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
        logger.info(f"🧭 Router output: {parsed}")
 
        if isinstance(parsed, dict):
            router_decision.update(parsed)

        # 🚦 INIT ADD PROPERTY FLOW
        # --------------------------------------------------
        if (
            router_decision.get("use_tool")
            and router_decision.get("tool_name") == "property"
            and router_decision.get("tool_arguments", {}).get("action") == "add"
        ):
            context.pending_action = "add_property"

            # Merge ALL router extracted fields safely
            router_args = router_decision.get("tool_arguments", {})
            for key, value in {
            "title": router_args.get("title"),
            "city": router_args.get("city"),
            "locality": router_args.get("locality"),
            "purpose": router_args.get("purpose"),
            "price": router_args.get("price") or router_args.get("budget"),
            "bhk": router_args.get("bhk"),
            "area_sqft": router_args.get("area_sqft") or router_args.get("sqt"),
            "owner_name": router_args.get("owner_name"),
            "contact_phone": router_args.get("contact") or router_args.get("contact_phone"),
        }.items():
                if value is not None and key not in context.partial_payload:
                    context.partial_payload[key] = value
 
    except Exception as e:
        if GuardrailTripwire and isinstance(e, GuardrailTripwire) and e.tripwire_triggered:
            logger.warning("🚫 Router guardrail triggered")
            yield {"type": "token", "value": "Sorry, I can’t help with that request."}
            return
 
        logger.exception("❌ Router failed")
 
       # --------------------------------------------------

    # 4️⃣ MEMORY WRITE (FIXED)

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

            action_type = memory_action.get("action")
 
            logger.info("🧠 Memory action: %s", memory_action)
 
            # 🔧 FIX: allow update & delete (no dedupe)

            if action_type in {"save", "update", "delete"}:

                yield {"type": "memory_event", "payload": memory_action}
 
        except Exception:

            logger.exception("❌ Memory write failed")
    
    # --------------------------------------------------
    # 🧩 PROPERTY SLOT FILLING (MUST BE HERE)
    # --------------------------------------------------
    if context and context.pending_action == "add_property":
        missing = get_missing_fields(
            context.partial_payload,
            REQUIRED_PROPERTY_FIELDS
        )

        if missing:
            pretty = "\n".join(
                f"• {f.replace('_', ' ').title()}"
                for f in missing
            )

            yield {
                "type": "token",
                "value": (
                    "Sure 👍 I’ll help you add the property.\n\n"
                    "Please provide the following details:\n"
                    f"{pretty}"
                ),
            }
            return

 
    # --------------------------------------------------
    # 5️⃣ TOOL EXECUTION (WITH VALIDATION)
    # --------------------------------------------------
    tool_context = {}

    can_execute_property_add = (
        context.pending_action == "add_property"
        and not get_missing_fields(
            context.partial_payload,
            REQUIRED_PROPERTY_FIELDS
        )
    )

    if can_execute_property_add:
        logger.info("🛠️ Executing property.add")

    if not getattr(context, "auth_token", None):
        yield {
            "type": "token",
            "value": "🔐 Please log in to add a property."
        }
        return
    
    tool_context = ToolExecutor.execute(
        "property",
        {
            "action": "add",
            "payload": context.partial_payload,
            "auth_token": context.auth_token,
        }
    )

    if tool_context.get("error"):
        yield {
            "type": "token",
            "value": f"❌ Failed to add property: {tool_context.get('error')}"
        }
        return
    
    if tool_context.get("property_id"):
        yield {
            "type": "token",
            "value": (
                "✅ Property added successfully!\n"
                f"Property ID: {tool_context['property_id']}"
            )
        }

        # 🧹 CLEAR STATE
        context.pending_action = None
        context.partial_payload = {}
        return

    logger.info("🧾 Property tool response: %s", tool_context)
 
    if router_decision.get("use_tool") or can_execute_property_add:
        try:
            logger.info("🛠️ Tool execution started")
 
            tool_raw = await Runner.run(
                tool_agent,
                router_input,
                context=context,
                max_turns=1,
            )
 
            tool_payload = safe_json_loads(tool_raw.final_output, default={})
            logger.info(f"🛠️ Tool payload: {tool_payload}")
 
            tool_name = tool_payload.get("tool")
            tool_arguments = tool_payload.get("arguments", {})

            if can_execute_property_add:
                tool_name = "property"
                tool_arguments = {
                    "action": "add",
                    "payload": context.partial_payload,
                }

            action = tool_arguments.get("action")
 
            # 🔍 PROPERTY VALIDATION BEFORE SAVE
            if tool_name == "property" and action == "add":
                payload = tool_arguments.get("payload", {})
                missing_fields = get_missing_fields(
                    payload, REQUIRED_PROPERTY_FIELDS
                )
 
                if missing_fields:
                    logger.warning(
                        f"⛔ Missing property fields: {missing_fields}"
                    )
 
                    pretty_fields = ", ".join(missing_fields)
 
                    yield {
                        "type": "token",
                        "value": (
                            f"Before I save the property, I still need: **{pretty_fields}**.\n"
                            "Please provide these details."
                        ),
                    }
                    return
 
            # 🔐 JWT INJECTION
            auth_token = None
            if context and hasattr(context, "auth_token"):
                auth_token = context.auth_token
 
            if auth_token:
                masked = auth_token[:15] + "..."
                logger.info(f"🔐 JWT attached: {masked}")
                tool_arguments["auth_token"] = auth_token
            else:
                logger.warning("⚠️ No JWT found for tool call")

            # 🔁 Normalize property budget field
            if tool_name == "property":
                if "max_budget" in tool_arguments and "budget" not in tool_arguments:
                    tool_arguments["budget"] = tool_arguments.pop("max_budget")
 
            tool_context = ToolExecutor.execute(
                tool_name,
                tool_arguments,
            )

            if can_execute_property_add and not tool_context.get("error"):
                context.pending_action = None
                context.partial_payload = {}
 
            logger.info(f"🛠️ Tool response: {tool_context}")
 
            if hasattr(tool_context, "model_dump"):
                tool_context = tool_context.model_dump()
 
        except Exception:
            logger.exception("❌ Tool execution failed")
            tool_context = {"error": "Tool execution failed"}
 
    # --------------------------------------------------
    # 6️⃣ REASONING
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
    # 7️⃣ FALLBACK
    # --------------------------------------------------
    if not emitted:
        logger.warning("⚠️ No tokens emitted")
        yield {"type": "token", "value": "I’m here 😊 What would you like to do next?"}
 
    logger.info("✅ Orchestrator completed")
 
 

