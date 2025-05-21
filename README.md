# Whisper Transcription Service

A FastAPI-based microservice that provides audio transcription capabilities using OpenAI's Whisper model. This service can transcribe various audio formats and automatically detects the language of the input.

## Features

- Transcribes audio files using OpenAI's Whisper model
- Supports multiple audio formats (MP3, WAV, OGG, M4A, WEBM, OGA)
- Automatic language detection
- Automatic audio format conversion to WAV when needed
- Docker support for easy deployment
- Configurable Whisper model size (tiny, base, small, medium, large)
- GPU acceleration when available (CUDA)

## Prerequisites

- Python 3.12 or later
- FFmpeg (for audio processing)
- Docker (optional, for containerized deployment)
- Sufficient system resources:
  - CPU: At least 2 cores recommended
  - RAM: Minimum 4GB, 8GB+ recommended
  - GPU: Optional but recommended for faster transcription (CUDA compatible)
  - Storage: At least 1GB free space for model files

## Installation

### Local Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/transcribing-service.git
cd transcribing-service
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Docker Installation

Build the Docker image:
```bash
docker build -t whisper-transcription-service .
```

## Configuration

The service can be configured using environment variables:

- `AUDIO_DIR`: Directory containing source audio files (default: `/app/audio`)
- `WAV_DIR`: Directory for temporary WAV files (default: `/app/wav`)
- `WHISPER_MODEL`: Whisper model size (default: `base`, options: tiny, base, small, medium, large)
- `LOG_LEVEL`: Logging level (default: `INFO`)

Note: This service uses the open-source version of Whisper that runs locally. No API keys are required.

## Usage

### Running Locally

1. Start the service:
```bash
python app/app.py
```

The service will be available at `http://localhost:7020`

### Running with Docker

```bash
docker run -p 7020:7020 \
  -v /path/to/audio:/app/audio \
  -v /path/to/wav:/app/wav \
  -e WHISPER_MODEL=base \
  whisper-transcription-service
```

### API Endpoints

#### POST /transcribe

Transcribes an audio file.

Request body:
```json
{
    "filename": "example.mp3"
}
```

Response:
```json
{
    "text": "Transcribed text content...",
    "language": "en"
}
```

## Supported Audio Formats

- MP3 (.mp3)
- WAV (.wav)
- OGG (.ogg)
- M4A (.m4a)
- WEBM (.webm)
- OGA (.oga)

## Model Sizes and Requirements

The service supports different Whisper model sizes with varying resource requirements:

- `tiny`: ~1GB RAM, fastest but least accurate
- `base`: ~1GB RAM, good balance of speed and accuracy
- `small`: ~2GB RAM, better accuracy
- `medium`: ~5GB RAM, high accuracy
- `large`: ~10GB RAM, highest accuracy

Choose the model size based on your available system resources and accuracy requirements.

## License

This project is licensed under the terms of the included LICENSE file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
