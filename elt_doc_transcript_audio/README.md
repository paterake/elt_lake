# elt-doc-transcript-audio

ELT module for transcribing audio recordings and extracting meeting discussions using OpenAI Whisper.

## Setup

### Quick Run

```bash
cd elt_doc_transcript_audio
uv sync --reinstall
```

### Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) package manager

### Create and sync the virtual environment

```bash
cd elt_doc_transcript_audio
uv sync
```

This creates a `.venv/` directory and installs all dependencies.

### Running the transcription script

```bash
# Basic transcription
uv run python scripts/transcribe_audio.py /path/to/audio.m4a

# Extract discussion up to DPIA topic
uv run python scripts/transcribe_audio.py /path/to/audio.m4a --extract --stop-at DPIA --title "Data Archival Discussion"

# Use a different model (tiny, base, small, medium, large)
uv run python scripts/transcribe_audio.py /path/to/audio.m4a --model small

# Specify output path
uv run python scripts/transcribe_audio.py /path/to/audio.m4a -o /path/to/output.txt

# Verbose output
uv run python scripts/transcribe_audio.py /path/to/audio.m4a -v
```

### Running tests

```bash
uv run pytest test/ -v
```

### Adding dependencies

```bash
# Add a runtime dependency
uv add some-package

# Add a dev dependency
uv add --group dev black
```

## Features

- Transcribe audio files using OpenAI Whisper
- Extract discussions up to a specific topic (e.g., stop at DPIA discussion)
- Multiple model sizes for different accuracy/speed tradeoffs
- CLI interface for easy usage

## Usage

### Using the AudioTranscriber class

```python
from elt_doc_transcript_audio import AudioTranscriber

# Create transcriber
transcriber = AudioTranscriber(model_name="base", verbose=True)

# Full transcription
result = transcriber.transcribe(
    audio_path="/path/to/audio.m4a",
    output_path="/path/to/transcript.txt",
)

# Transcribe with extraction (stop at specific topic)
result = transcriber.transcribe_with_extraction(
    audio_path="/path/to/audio.m4a",
    output_path="/path/to/extracted_transcript.txt",
    stop_at_topic="DPIA",
    topic_title="Data Archival and Data Retention Discussion",
)

print(f"DPIA discussion found: {result.dpia_found}")
print(f"Extracted transcript:\n{result.extracted_transcript}")
```

### CLI Options

| Option | Description |
|--------|-------------|
| `audio_path` | Path to the audio file (required) |
| `-o, --output` | Output path for transcript (default: same dir as audio) |
| `--model` | Whisper model: tiny, base, small, medium, large (default: base) |
| `--extract` | Extract discussion up to a stop topic |
| `--stop-at` | Topic keyword to stop at (default: DPIA) |
| `--title` | Title for extracted transcript |
| `-v, --verbose` | Show verbose output |

## Models

| Model | Parameters | English-only | Multilingual | Speed | Accuracy |
|-------|------------|--------------|--------------|-------|----------|
| tiny | 39 M | ✓ | ✓ | Fastest | Lower |
| base | 74 M | ✓ | ✓ | Fast | Good |
| small | 244 M | ✓ | ✓ | Medium | Better |
| medium | 769 M | ✓ | ✓ | Slow | High |
| large | 1550 M | ✓ | ✓ | Slowest | Highest |

## Dependencies

- `openai-whisper>=20250625` - Audio transcription using Whisper
