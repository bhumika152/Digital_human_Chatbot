import httpx
import json
import logging
import time

logger = logging.getLogger("chat_backend.digital_human_client")


class DigitalHumanClient:
    def __init__(self, base_url: str):
        if not base_url:
            raise RuntimeError("DIGITAL_HUMAN_BASE_URL not set")
        self.base_url = base_url.rstrip("/")

    async def stream_chat(
        self,
        *,
        user_input,
        llm_context,
        flags,
        request_id: str,
        auth_token: str,
    ):
        payload = {
            "llm_context": llm_context,
            "flags": flags,
        }

        headers = {
            "X-Request-Id": request_id
        }

        if auth_token:
            headers["Authorization"] = auth_token  # 🔑 FORWARD TOKEN

        start = time.perf_counter()

        logger.info(
            "➡️ Calling Digital Human | request_id=%s",
            request_id,
        )

        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(
                connect=10.0,
                read=None,   # streaming
                write=10.0,
                pool=10.0,
            ),
        ) as client:
            try:
                async with client.stream(
                    "POST",
                    "/v1/chat/stream",
                    json=payload,
                    headers=headers,
                ) as response:

                    response.raise_for_status()

                    logger.info(
                        "✅ Digital Human connected | status=%s | request_id=%s",
                        response.status_code,
                        request_id,
                    )

                    async for line in response.aiter_lines():
                        if not line.startswith("data:"):
                            continue

                        data = line.removeprefix("data:").strip()
                        yield json.loads(data)

            except Exception:
                logger.exception(
                    "🔥 Digital Human stream failed | request_id=%s",
                    request_id,
                )
                raise

            finally:
                elapsed = round(time.perf_counter() - start, 2)
                logger.info(
                    "⬅️ Digital Human stream closed | time=%ss | request_id=%s",
                    elapsed,
                    request_id,
                )
