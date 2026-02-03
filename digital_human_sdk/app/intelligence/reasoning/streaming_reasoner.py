from openai import AsyncOpenAI
from pathlib import Path
import json

client = AsyncOpenAI()

PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "reasoning.md"
SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")


async def stream_reasoning_answer(reasoning_input: dict):
    """
    Streams the FINAL reasoning answer (token-by-token).
    """

    response = await client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": json.dumps(reasoning_input),
            },
        ],
        stream=True,
    )

    async for event in response:
        if event.type == "response.output_text.delta":
            yield event.delta
