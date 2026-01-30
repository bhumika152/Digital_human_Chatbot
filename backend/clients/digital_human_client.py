
import httpx
import json
import logging

logger = logging.getLogger(__name__)


class DigitalHumanClient:
    def __init__(self, base_url: str):
        if not base_url:
            raise RuntimeError("DIGITAL_HUMAN_BASE_URL not set")
        self.base_url = base_url.rstrip("/")

    async def stream_chat(self, *, user_input, llm_context, flags):
        payload = {
            "user_input": user_input,
            "llm_context": llm_context,
            "flags": flags,
        }

        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(
                connect=10.0,
                read=None,
                write=10.0,
                pool=10.0,
            ),
        ) as client:
            async with client.stream(
                "POST",
                "/v1/chat/stream",
                json=payload,
            ) as response:

                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line.startswith("data:"):
                        continue

                    payload = line.removeprefix("data:").strip()
                    yield json.loads(payload)
