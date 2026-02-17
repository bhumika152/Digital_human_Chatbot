import uuid
import os
import json
import whisper
import requests
import re
import unicodedata
import io
import subprocess
import numpy as np
import base64

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

from TTS.api import TTS


# ==========================================================
# Router
# ==========================================================
router = APIRouter(prefix="/voice", tags=["voice"])


# ==========================================================
# Config
# ==========================================================
DIGITAL_HUMAN_BASE_URL = os.getenv(
    "DIGITAL_HUMAN_BASE_URL",
    "http://127.0.0.1:8001",
)


# ==========================================================
# Load Models (ONCE)
# ==========================================================
print("🔊 Loading Whisper...")
stt_model = whisper.load_model("base")

print("🔊 Loading TTS...")
tts_model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")


# ==========================================================
# TTS Text Cleaner
# ==========================================================
def clean_text_for_tts(text: str) -> str:

    text = re.sub(r'[\*\#\>\-\_`~]', ' ', text)
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1', text)
    text = re.sub(r'\*{1,2}(.+?)\*{1,2}', r'\1', text)
    text = re.sub(r'http\S+', '', text)

    text = unicodedata.normalize('NFKD', text)\
        .encode('ascii', 'ignore')\
        .decode('ascii')

    text = re.sub(r'[\[\]\(\)\{\}]', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9.,!?\'" ]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# ==========================================================
# Audio Bytes → NumPy (For Whisper)
# ==========================================================
def bytes_to_numpy(audio_bytes: bytes) -> np.ndarray:

    cmd = [
        "ffmpeg",
        "-i", "pipe:0",
        "-f", "s16le",
        "-ac", "1",
        "-ar", "16000",
        "pipe:1"
    ]

    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    out, err = process.communicate(audio_bytes)

    if process.returncode != 0:
        raise RuntimeError(err.decode())

    audio = np.frombuffer(out, np.int16).astype(np.float32) / 32768.0

    return audio


# ==========================================================
# API
# ==========================================================
@router.post("")
async def voice_handler(file: UploadFile = File(...)):

    try:

        # 1️⃣ Read audio
        audio_bytes = await file.read()

        # 2️⃣ Convert for Whisper
        audio_np = bytes_to_numpy(audio_bytes)

        # 3️⃣ STT
        result = stt_model.transcribe(audio_np)

        user_text = result.get("text", "").strip()

        if not user_text:
            return JSONResponse(
                status_code=400,
                content={"error": "No speech detected"},
            )

        print("📝 User:", user_text)

        # 4️⃣ Call Digital Human
        response = requests.post(
            f"{DIGITAL_HUMAN_BASE_URL}/v1/chat/stream",
            json={
                "llm_context": [
                    {"role": "user", "content": user_text}
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
            raise RuntimeError("Digital Human failed")

        reply_text = ""

        for line in response.iter_lines():

            if not line:
                continue

            decoded = line.decode("utf-8").strip()

            if not decoded.startswith("data:"):
                continue

            payload = decoded.removeprefix("data:").strip()
            data = json.loads(payload)

            if data.get("type") == "token":
                reply_text += data.get("value", "")

        if not reply_text.strip():
            raise RuntimeError("Empty reply")

        print("🤖 AI:", reply_text)

        # 5️⃣ Clean text
        clean_reply = clean_text_for_tts(reply_text)

        # Limit length for speed
        clean_reply = clean_reply[:400]

        # 6️⃣ TTS
        wav = tts_model.tts(clean_reply)

        audio_buffer = io.BytesIO()
        tts_model.synthesizer.save_wav(wav, audio_buffer)

        # 7️⃣ Convert audio → base64
        audio_base64 = base64.b64encode(
            audio_buffer.getvalue()
        ).decode("utf-8")
        # 8️⃣ Send JSON (UI Friendly)
        return {
            "user_text": user_text,
            "reply_text": reply_text,
            "audio": audio_base64
        }
    except Exception as e:

        print("❌ VOICE ERROR:", e)

        return JSONResponse(
            status_code=500,
            content={"error": "Voice processing failed"},
        )
