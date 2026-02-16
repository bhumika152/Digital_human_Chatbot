class PersonaPlexAdapter:
    """
    PersonaPlex-compatible speech adapter
    (PoC backend = existing TTS)
    """

    def __init__(self, tts_model):
        self.tts_model = tts_model

    async def speak(self, text: str, emotion: str = "neutral") -> bytes:
        """
        Converts FINAL orchestrator text → audio
        """
        out_path = "digital_human_sdk/app/temp/personaplex_out.wav"

        # PoC: use existing TTS
        self.tts_model.tts_to_file(
            text=text,
            file_path=out_path,
        )

        with open(out_path, "rb") as f:
            return f.read()
