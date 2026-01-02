from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def chat_completion(messages, temperature=0.3):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content
