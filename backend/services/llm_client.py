from litellm import completion
 
SUMMARY_MODEL = "gemini/gemini-2.5-flash"
 
def call_llm(prompt: str) -> str:
    """
    Lightweight LLM call for background tasks like summarization.
    No agents. No tools. No streaming.
    """
 
    response = completion(
        model=SUMMARY_MODEL,
        provider="gemini",   # 🔑 REQUIRED
        messages=[
            {
                "role": "system",
                "content": "You are a precise memory compression engine."
            },
            {
                "role": "user",
                "content": prompt
            },
        ],
        temperature=0.2,
        max_tokens=400,
    )
 
    return response.choices[0].message.content
 
 