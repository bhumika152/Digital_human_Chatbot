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
# INPUT GUARDRAIL (HARD BLOCK ONLY)
# -------------------------------
@input_guardrail(name="Input Safety Guardrail")
def input_safety(ctx, agent, raw_input):
    if not raw_input:
        return GuardrailFunctionOutput(
            tripwire_triggered=False,
            output_info="Empty input allowed",
        )

    text = str(raw_input).strip().lower()

    # ✅ Allow greetings / very short input
    if len(text.split()) <= 2:
        return GuardrailFunctionOutput(
            tripwire_triggered=False,
            output_info="Short safe input",
        )

    # 🚫 Prompt injection (STRICT)
    if matches_blocked_pattern(text):
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info={
                "message": "I can’t help with that request."
            },
        )

    # 🚫 Explicit dangerous HOW-TO only
    for topic in BLOCKED_TOPICS:
        if topic in text and any(k in text for k in ["how to", "steps", "make", "build"]):
            return GuardrailFunctionOutput(
                tripwire_triggered=True,
                output_info={
                    "message": "I can’t help with that topic."
                },
            )

    # ✅ Everything else allowed
    return GuardrailFunctionOutput(
        tripwire_triggered=False,
        output_info="Input safe",
    )


# -------------------------------
# OUTPUT GUARDRAIL (POST-REASONING)
# -------------------------------
@output_guardrail(name="Output Safety Guardrail")
def output_safety(ctx, agent, output):
    text = str(output)

    # 🚫 Output size limit
    if len(text) > MAX_OUTPUT_CHARS:
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info={
                "message": "Response was too long to safely display."
            },
        )

    # 🚫 Policy / system leakage
    lowered = text.lower()
    if any(k in lowered for k in ["system prompt", "developer message", "openai policy"]):
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info={
                "message": "I can’t share internal system details."
            },
        )

    return GuardrailFunctionOutput(
        tripwire_triggered=False,
        output_info="Output safe",
    )
