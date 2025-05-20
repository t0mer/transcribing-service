# -------- Whisper-based transcription service image --------
FROM python:3.12-slim

# Install ffmpeg for pydub & Whisper
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Copy project
WORKDIR /app
COPY requirements.txt .

# Default audio directories (override with -e)
ENV AUDIO_DIR=/app/audio \
    WAV_DIR=/app/wav

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app

CMD ["python", "app.py"]

