from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from types import SimpleNamespace

import json

from digital_human_sdk.app.orchestrator import run_digital_human_chat

router = APIRouter(prefix="/v1/chat", tags=["digital-human"])

@router.post("/stream")
async def stream_chat(payload: dict):
    #user_input = payload["user_input"]
    llm_context = payload["llm_context"]
    flags = payload["flags"]


    context = SimpleNamespace(
    user_id=flags.get("user_id"),
    session_id=flags.get("session_id"),
    enable_memory=flags.get("enable_memory", True),
    enable_tools=flags.get("enable_tools", True),
    enable_rag=flags.get("enable_rag", True),
    router_context=flags.get("router_context"),
    memory_data=flags.get("memory_data", []),
    kb_data=flags.get("kb_data", []),
    kb_found=flags.get("kb_found", False),
)
    async def event_stream():
        try:
            async for event in run_digital_human_chat(
                llm_messages=llm_context,
                context=context,
            ):
                yield f"data: {json.dumps(event)}\n\n"

        except Exception as exc:
            # 🔥 NEVER let the stream die silently
            error_event = {
                "type": "error",
                "message": str(exc),
            }
            yield f"data: {json.dumps(error_event)}\n\n"


    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )
