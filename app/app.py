"""
FastAPI micro-service that transcribes audio files with OpenAI Whisper.

Workflow
========
1. Validate that the requested file exists inside AUDIO_DIR.
2. Ensure the file extension is one Whisper can handle.
3. Convert the original audio to WAV with **pydub / ffmpeg** when needed.
4. Transcribe the WAV file with Whisper (CUDA if available, otherwise CPU).
5. Return the recognised text and the detected language code.

Environment variables
---------------------
AUDIO_DIR       – directory that already contains the source audio files
WAV_DIR         – directory where temporary WAV files will be written
WHISPER_MODEL   – Whisper model size: tiny | base | small | medium | large
LOG_LEVEL       – (optional) log level for Loguru, default INFO
"""

import os
import sys
from typing import Set
import uvicorn
import torch
import whisper
from fastapi import FastAPI, HTTPException
from loguru import logger
from pydantic import BaseModel
from pydub import AudioSegment

# --------------------------------------------------------------------------- #
# Logging setup (stdout so Docker captures it)
# --------------------------------------------------------------------------- #
logger.remove()
logger.add(sys.stdout, level=os.getenv("LOG_LEVEL", "INFO"))

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
AUDIO_DIR: str = os.getenv("AUDIO_DIR", "/data/audio")
WAV_DIR: str = os.getenv("WAV_DIR", "/data/wav")
WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")

SUPPORTED_AUDIO_EXT: Set[str] = {".mp3", ".wav", ".ogg",
                                 ".m4a", ".webm", ".oga"}

os.makedirs(WAV_DIR, exist_ok=True)  # make sure temp directory exists

device = "cuda" if torch.cuda.is_available() else "cpu"
logger.info("Whisper will run on device: {}", device)

logger.info("Loading Whisper model '{}' …", WHISPER_MODEL)
model = whisper.load_model(WHISPER_MODEL, device=device)
logger.success("Model loaded")

# --------------------------------------------------------------------------- #
# FastAPI application
# --------------------------------------------------------------------------- #
app = FastAPI(title="Whisper Transcription Service")


class AudioFileRequest(BaseModel):
    """Schema for the POST /transcribe payload."""
    filename: str


@app.post("/transcribe")
async def transcribe_audio_file(request: AudioFileRequest):
    """
    Convert an audio file to WAV (if necessary) and transcribe it.

    Returns
    -------
    JSON
        {"text": "...", "language": "xx"}
    """
    filename = request.filename
    filepath = os.path.join(AUDIO_DIR, filename)
    logger.debug("Incoming transcription request for '{}'", filepath)

    # 1. File exists?
    if not os.path.isfile(filepath):
        logger.warning("File not found: {}", filepath)
        raise HTTPException(status_code=404, detail="File not found")

    # 2. Supported format?
    ext = os.path.splitext(filename)[1].lower()
    if ext not in SUPPORTED_AUDIO_EXT:
        logger.warning("Unsupported file format: {}", ext)
        raise HTTPException(
            status_code=400, detail=f"Unsupported file format: {ext}"
        )

    # 3. Convert to WAV when required
    if ext != ".wav":
        wav_path = os.path.join(
            WAV_DIR, f"{os.path.splitext(filename)[0]}.wav")
        logger.debug("Converting '{}' ➜ '{}'", filepath, wav_path)
        try:
            audio = AudioSegment.from_file(filepath)
            audio.export(wav_path, format="wav")
        except Exception as e:
            logger.exception("Audio conversion failed")
            raise HTTPException(
                status_code=500, detail=f"Audio conversion failed: {e}"
            )
    else:
        wav_path = filepath

    # 4. Transcribe
    logger.info("Transcribing '{}'", wav_path)
    try:
        result = model.transcribe(wav_path)
        logger.success("Transcription finished")
        return {"text": result["text"], "language": result["language"]}
    except Exception as e:
        logger.exception("Transcription failed")
        raise HTTPException(
            status_code=500, detail=f"Transcription failed: {e}"
        )


# --------------------------------------------------------------------------- #
# Local entrypoint:  `python main.py`
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    logger.info("Starting the service")
    uvicorn.run(app, host="0.0.0.0", port=7020)
