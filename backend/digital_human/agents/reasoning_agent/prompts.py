# reasoning_agent/prompts.py

REASONING_PROMPT = f"""
You are an AI reasoning engine.

Your task:
1. Understand the user's intent.
2. Classify intent into ONE of the following:
   - learning_goal
   - information_request
   - comparison_request
   - user_preference
   - general_chat
3. Extract the topic if present.
4. Assign a confidence score between 0 and 1.

Return ONLY valid JSON in this format:
{{
  "intent_type": "string",
  "topic": "string or null",
  "confidence": 0.0
}}

User message:
"{{user_input}}"
"""

