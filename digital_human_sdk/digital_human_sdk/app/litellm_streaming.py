from litellm import completion
#from digital_human_sdk.app.intelligence.models.litellm_model import get_model_name
async def stream_llm_response(prompt: str):
    """
    True token-wise streaming from LiteLLM
    """
    response = completion(
        model="gemini/gemini-2.5-flash",
        provider= "gemini",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    for chunk in response:
        try:
            delta = chunk["choices"][0]["delta"]
            if "content" in delta:
                yield delta["content"]
        except Exception:
            continue
