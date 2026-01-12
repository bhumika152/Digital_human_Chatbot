from agents import (
    GuardrailFunctionOutput,
    input_guardrail,
    output_guardrail,
)

from .config import (
    matches_blocked_pattern,
    BLOCKED_TOPICS,
    MAX_OUTPUT_CHARS,
)


# -------------------------------
# INPUT GUARDRAIL
# -------------------------------
@input_guardrail(name="Input Safety Guardrail")
def input_safety(ctx, agent, raw_input):
    text = str(raw_input).lower()

    # Prompt injection detection
    if matches_blocked_pattern(text):
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info="Prompt injection attempt detected",
        )

    # Blocked topic detection
    for topic in BLOCKED_TOPICS:
        if topic in text:
            return GuardrailFunctionOutput(
                tripwire_triggered=True,
                output_info=f"Blocked topic: {topic}",
            )

    return GuardrailFunctionOutput(
        tripwire_triggered=False,
        output_info="Input safe",
    )


# -------------------------------
# OUTPUT GUARDRAIL
# -------------------------------
@output_guardrail(name="Output Safety Guardrail")
def output_safety(ctx, agent, output):
    text = str(output)

    # Output length control
    if len(text) > MAX_OUTPUT_CHARS:
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info="Output too long (possible data leakage)",
        )

    # Prevent policy disclosure
    if "openai policy" in text.lower():
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info="Policy disclosure attempt",
        )

    return GuardrailFunctionOutput(
        tripwire_triggered=False,
        output_info="Output safe",
    )


