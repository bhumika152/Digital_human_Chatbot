# def extract_memory_intent(user_input: str) -> dict:
#     if "goal" in user_input.lower():
#         return {
#             "action": "save",
#             "key": "goal",
#             "value": user_input.split("goal is")[-1].strip(),
#             "confidence": 0.9
#         }
#     elif "prefer" in user_input.lower():
#         return {
#             "action": "save",
#             "key": "preference",
#             "value": user_input.split("prefer")[-1].strip(),
#             "confidence": 0.85
#         }
#     return None


def extract_memory_intent(user_input: str):
    if "goal is" in user_input:
        return {
            "action": "save",
            "key": "goal",
            "value": user_input.split("goal is")[-1].strip(),
            "confidence": 0.9
        }

    if "prefer" in user_input:
        return {
            "action": "save",
            "key": "preference",
            "value": user_input.split("prefer")[-1].strip(),
            "confidence": 0.85
        }

    return None
