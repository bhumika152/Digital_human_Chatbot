from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json

from digital_human_sdk.app.main import run_digital_human_chat

router = APIRouter(prefix="/v1/chat", tags=["digital-human"])


@router.post("/stream")
async def stream_chat(payload: dict):
    user_input = payload["user_input"]
    llm_context = payload["llm_context"]
    flags = payload["flags"]

    async def event_stream():
        async for event in run_digital_human_chat(
            user_input=user_input,
            llm_context=llm_context,
            context=None,  # context rebuilt internally if needed
        ):
            yield json.dumps(event) + "\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )
