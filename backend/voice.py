import uuid
import os
import json
import whisper
import requests
from pathlib import Path

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

from TTS.api import TTS


# ==========================================================
# Router
# ==========================================================
router = APIRouter(prefix="/voice", tags=["voice"])


# ==========================================================
# Paths
# ==========================================================
BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)


# ==========================================================
# Config
# ==========================================================
DIGITAL_HUMAN_BASE_URL = os.getenv(
    "DIGITAL_HUMAN_BASE_URL",
    "http://127.0.0.1:8001",   # Digital Human service
)


# ==========================================================
# Load Models (ONCE)
# ==========================================================
print("🔊 Loading Whisper...")
stt_model = whisper.load_model("base")

print("🔊 Loading TTS (PoC)...")
tts_model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")


# ==========================================================
# API
# ==========================================================
@router.post("")
async def voice_handler(file: UploadFile = File(...)):
    try:
        audio_id = str(uuid.uuid4())

        input_path = TEMP_DIR / f"{audio_id}.wav"
        output_path = TEMP_DIR / f"{audio_id}_out.wav"

        # --------------------
        # Save uploaded audio
        # --------------------
        with open(input_path, "wb") as f:
            f.write(await file.read())

        print("✅ Saved audio:", input_path)

        # --------------------
        # Speech → Text (STT)
        # --------------------
        result = stt_model.transcribe(str(input_path))
        user_text = result.get("text", "").strip()

        if not user_text:
            return JSONResponse(
                status_code=400,
                content={"error": "No speech detected"},
            )

        print("📝 Recognized:", user_text)

        # --------------------
        # 🧠 Digital Human (STREAMING)
        # --------------------
        response = requests.post(
            f"{DIGITAL_HUMAN_BASE_URL}/v1/chat/stream",
            json={
                "llm_context": [
                    {
                        "role": "user",
                        "content": user_text
                    }
                ],
                "flags": {
                    "user_id": "voice_poc",
                    "session_id": str(uuid.uuid4()),
                    "enable_memory": True,
                    "enable_tools": True,
                    "enable_rag": True
                }
            },
            stream=True,
            timeout=60,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Digital Human failed: {response.status_code} {response.text}"
            )

        reply_text = ""

        for line in response.iter_lines():
            if not line:
                continue

            decoded = line.decode("utf-8").strip()

            # SSE format: "data: {...}"
            if not decoded.startswith("data:"):
                continue

            try:
                payload = decoded.removeprefix("data:").strip()
                data = json.loads(payload)

                if data.get("type") == "token":
                    reply_text += data.get("value", "")

            except Exception:
                continue

        if not reply_text.strip():
            raise RuntimeError("Empty reply from Digital Human")

        print("🤖 AI Reply:", reply_text)

        # --------------------
        # 🔊 Text → Speech (PoC / PersonaPlex hook)
        # --------------------
        tts_model.tts_to_file(
            text=reply_text,
            file_path=str(output_path),
        )

        print("🔊 Generated:", output_path)

        return {
            "user_text": user_text,
            "reply_text": reply_text,
            "audio_url": f"temp/{output_path.name}",
        }

    except Exception as e:
        print("❌ VOICE ERROR:", e)

        return JSONResponse(
            status_code=500,
            content={"error": "Voice processing failed"},
        )