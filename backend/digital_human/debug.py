from dotenv import load_dotenv
load_dotenv()

from digital_human.service import run_digital_human_chat


def run_cli():
    print("🤖 Digital Human (CLI Mode)")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye 👋")
            break

        result = run_digital_human_chat(user_input)

        print("\nAssistant:", result["response"])
        print("\nmemory_intent:", result["memory_intent"])
        print("-" * 60)


if __name__ == "__main__":
    run_cli()
