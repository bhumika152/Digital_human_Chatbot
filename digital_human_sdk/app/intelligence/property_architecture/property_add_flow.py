from property_validator import find_missing_fields
from property_fields import (
    PROPERTY_DEFAULTS,
    PROPERTY_QUESTIONS,
)
from app.intelligence.tools.tool_executor import ToolExecutor

def handle_property_add_flow(
    *,
    context,
    tool_arguments: dict,
):
    property_draft = context.session_state.get("property_draft", {})
    incoming_payload = tool_arguments.get("payload", {})

    property_draft.update(incoming_payload)
    property_draft["is_legal"] = True

    context.session_state["property_draft"] = property_draft

    missing = find_missing_fields(property_draft)

    if missing:
        field = missing[0]
        return {
            "type": "token",
            "value": PROPERTY_QUESTIONS[field],
        }

    # All fields present → save
    ToolExecutor.execute(
        "property",
        {
            "action": "add",
            "payload": property_draft,
            "auth_token": context.auth_token,
        },
    )

    context.session_state.pop("property_draft", None)

    return {
        "type": "token",
        "value": "✅ Property added successfully.",
    }
