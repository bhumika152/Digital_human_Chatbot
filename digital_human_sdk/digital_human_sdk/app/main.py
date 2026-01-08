from dotenv import load_dotenv
load_dotenv()
import asyncio
from app.intelligence.orchestration.orchestrator import Orchestrator

async def main():
    orchestrator = Orchestrator()

    print("---- TURN 1 ----")
    await orchestrator.handle_user_query(
        user_input="I prefer cold places like Manali and Shimla.",
        user_id=1,
    )

    print("---- TURN 2 ----")
    response = await orchestrator.handle_user_query(
        user_input="Suggest a destination for me",
        user_id=1,
    )

    print(response)


if __name__ == "__main__":
    asyncio.run(main())
