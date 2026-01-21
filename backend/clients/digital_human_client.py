# # clients/digital_human_client.py

# import httpx
# import json
# from typing import AsyncGenerator


# class DigitalHumanClient:
#     def __init__(self, base_url: str, timeout: int = 300):
#         self.base_url = base_url.rstrip("/")
#         self.timeout = timeout

#     async def stream_chat(
#         self,
#         *,
#         user_input: str,
#         llm_context: dict,
#         flags: dict,
#     ) -> AsyncGenerator[dict, None]:
#         """
#         Streams events from Digital Human service
#         """

#         payload = {
#             "user_input": user_input,
#             "llm_context": llm_context,
#             "flags": flags,
#         }

#         async with httpx.AsyncClient(timeout=self.timeout) as client:
#             async with client.stream(
#                 "POST",
#                 f"{self.base_url}/v1/chat/stream",
#                 json=payload,
#             ) as response:
#                 response.raise_for_status()

#                 async for line in response.aiter_lines():
#                     if not line:
#                         continue
#                     yield json.loads(line)
# backend/clients/digital_human_client.py

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
            timeout=httpx.Timeout(connect=10.0, read=None),
        ) as client:
            async with client.stream(
                "POST",
                "/v1/chat/stream",
                json=payload,
            ) as response:

                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line:
                        continue
                    yield json.loads(line)
