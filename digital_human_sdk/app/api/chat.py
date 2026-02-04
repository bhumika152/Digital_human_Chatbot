from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from types import SimpleNamespace
import json
import logging
import time

from app.orchestrator import run_digital_human_chat

router = APIRouter(prefix="/v1/chat", tags=["digital-human"])

logger = logging.getLogger("digital_human.api.chat")


@router.post("/stream")
async def stream_chat(payload: dict, request: Request):
    llm_context = payload["llm_context"]
    flags = payload["flags"]

    request_id = request.headers.get("X-Request-Id", "N/A")
    start_time = time.perf_counter()

    logger.info(
        "📩 Digital Human stream started | request_id=%s | session_id=%s",
        request_id,
        flags.get("session_id"),
    )

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
        event_count = 0
        try:
            async for event in run_digital_human_chat(
                llm_messages=llm_context,
                context=context,
            ):
                event_count += 1

                # DEBUG level (don’t flood prod logs)
                logger.debug(
                    "📤 Event emitted | type=%s | request_id=%s",
                    event.get("type"),
                    request_id,
                )

                yield f"data: {json.dumps(event)}\n\n"

        except Exception:
            logger.exception(
                "🔥 Digital Human stream crashed | request_id=%s",
                request_id,
            )

            error_event = {
                "type": "error",
                "message": "Digital Human stream failed",
            }
            yield f"data: {json.dumps(error_event)}\n\n"

        finally:
            elapsed = round(time.perf_counter() - start_time, 2)
            logger.info(
                "✅ Digital Human stream ended | events=%s | time=%ss | request_id=%s",
                event_count,
                elapsed,
                request_id,
            )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )
