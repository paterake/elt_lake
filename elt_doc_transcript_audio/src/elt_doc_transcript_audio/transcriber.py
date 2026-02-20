#!/usr/bin/env python3
"""Audio transcription module using OpenAI Whisper."""

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import whisper


@dataclass
class TranscriptionResult:
    """Result of a transcription operation."""

    full_transcript: str
    extracted_transcript: str
    dpia_found: bool
    output_path: Path


class AudioTranscriber:
    """Transcribe audio files and extract specific discussion topics."""

    def __init__(
        self,
        model_name: str = "base",
        verbose: bool = False,
    ):
        """Initialize the transcriber.

        Args:
            model_name: Whisper model to use (tiny, base, small, medium, large).
            verbose: Whether to show verbose output during transcription.
        """
        self.model_name = model_name
        self.verbose = verbose
        self._model: Optional[whisper.Whisper] = None

    def _load_model(self) -> whisper.Whisper:
        """Load the Whisper model."""
        if self._model is None:
            print(f"Loading Whisper model ({self.model_name})...")
            self._model = whisper.load_model(self.model_name)
        return self._model

    def transcribe(
        self,
        audio_path: str | Path,
        output_path: str | Path,
    ) -> TranscriptionResult:
        """Transcribe an audio file.

        Args:
            audio_path: Path to the audio file.
            output_path: Path to save the transcript.

        Returns:
            TranscriptionResult with the transcript data.
        """
        audio_path = Path(audio_path)
        output_path = Path(output_path)

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        model = self._load_model()

        print(f"Transcribing {audio_path}...")
        result = model.transcribe(str(audio_path), verbose=self.verbose)

        full_transcript = result["text"].strip()

        # Write the full transcript
        with open(output_path, "w") as f:
            f.write(full_transcript)

        print(f"Full transcript saved to: {output_path}")

        return TranscriptionResult(
            full_transcript=full_transcript,
            extracted_transcript=full_transcript,
            dpia_found=False,
            output_path=output_path,
        )

    def transcribe_with_extraction(
        self,
        audio_path: str | Path,
        output_path: str | Path,
        stop_at_topic: str = "DPIA",
        topic_title: str = "Data Archival and Data Retention Discussion",
    ) -> TranscriptionResult:
        """Transcribe audio and extract discussion up to a specific topic.

        Args:
            audio_path: Path to the audio file.
            output_path: Path to save the extracted transcript.
            stop_at_topic: Topic keyword to stop at (e.g., 'DPIA').
            topic_title: Title for the extracted transcript.

        Returns:
            TranscriptionResult with the extracted transcript data.
        """
        audio_path = Path(audio_path)
        output_path = Path(output_path)

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        model = self._load_model()

        print(f"Transcribing {audio_path}...")
        result = model.transcribe(str(audio_path), verbose=self.verbose)

        full_transcript = result["text"].strip()

        # Split into segments and extract up to the stop topic
        segments = full_transcript.split("\n")

        extracted_text = []
        topic_found = False
        stop_pattern = re.compile(rf"\b{re.escape(stop_at_topic)}\b", re.IGNORECASE)

        for segment in segments:
            if stop_pattern.search(segment):
                topic_found = True
                break
            extracted_text.append(segment)

        extracted_transcript = "\n".join(extracted_text).strip()

        # Write the extracted transcript
        with open(output_path, "w") as f:
            f.write(f"=== {topic_title} ===\n\n")
            f.write(extracted_transcript)
            if topic_found:
                f.write("\n\n[Transcript stopped at {stop_at_topic} discussion]")

        print(f"\nTranscript saved to: {output_path}")
        print(f"{stop_at_topic} discussion found: {topic_found}")

        return TranscriptionResult(
            full_transcript=full_transcript,
            extracted_transcript=extracted_transcript,
            dpia_found=topic_found,
            output_path=output_path,
        )
