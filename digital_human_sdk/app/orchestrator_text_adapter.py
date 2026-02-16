from app.orchestrator import run_digital_human_chat

async def run_orchestrator_and_collect_text(user_text: str, context):
    """
    Runs the orchestrator and collects final response text
    """
    messages = [{"role": "user", "content": user_text}]
    final_text = ""

    async for event in run_digital_human_chat(
        llm_messages=messages,
        context=context,
    ):
        if event["type"] == "token":
            final_text += event["value"]

    return final_text.strip()
