import asyncio
from app.main import run_digital_human_chat

async def test():
    user_input = "remember that i like cold places"
    chat_history = []
    user_config = {
        "memory_enabled": True,
        "tool_enabled": False,
    }

    print("\n--- DIGITAL HUMAN SDK TEST ---\n")

    async for event in run_digital_human_chat(
        user_input=user_input,
        chat_history=chat_history,
        user_config=user_config,
    ):
        if event["type"] == "token":
            print(event["value"], end="", flush=True)

        elif event["type"] == "memory_event":
            print("\n\n[MEMORY EVENT]")
            print(event["payload"])

    print("\n\n--- END ---")

asyncio.run(test())
