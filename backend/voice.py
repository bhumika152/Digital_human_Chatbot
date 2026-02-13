import uuid
import whisper
from pathlib import Path

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

from TTS.api import TTS


router = APIRouter(prefix="/voice", tags=["voice"])


# --------------------
# Paths
# --------------------

BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp"

TEMP_DIR.mkdir(exist_ok=True)


# --------------------
# Load Models
# --------------------

print("🔊 Loading Whisper...")
stt_model = whisper.load_model("base")

print("🔊 Loading TTS...")
tts_model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")


# --------------------
# API
# --------------------

@router.post("")
async def voice_handler(file: UploadFile = File(...)):

    try:
        audio_id = str(uuid.uuid4())

        input_path = TEMP_DIR / f"{audio_id}.wav"
        output_path = TEMP_DIR / f"{audio_id}_out.wav"

        # Save uploaded file
        with open(input_path, "wb") as f:
            f.write(await file.read())

        print("✅ Saved audio:", input_path)

        # Speech → Text
        result = stt_model.transcribe(str(input_path))
        user_text = result["text"].strip()

        if not user_text:
            return JSONResponse(
                status_code=400,
                content={"error": "No speech detected"},
            )

        print("📝 Recognized:", user_text)

        # Temporary reply
        reply_text = f"You said: {user_text}"

        # Text → Speech
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
