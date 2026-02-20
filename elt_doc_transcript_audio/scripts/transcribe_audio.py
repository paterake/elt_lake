#!/usr/bin/env python3
"""CLI script for transcribing audio files."""

import argparse
import sys
from pathlib import Path

from elt_doc_transcript_audio.transcriber import AudioTranscriber


def main():
    """Main entry point for the transcription CLI."""
    parser = argparse.ArgumentParser(
        description="Transcribe audio files and optionally extract discussions up to a specific topic."
    )
    parser.add_argument(
        "audio_path",
        type=str,
        help="Path to the audio file to transcribe",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Output path for the transcript (default: same directory as audio, _transcript suffix)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model to use (default: base)",
    )
    parser.add_argument(
        "--extract",
        action="store_true",
        help="Extract discussion up to a stop topic (e.g., DPIA)",
    )
    parser.add_argument(
        "--stop-at",
        type=str,
        default="DPIA",
        help="Topic keyword to stop extraction at (default: DPIA)",
    )
    parser.add_argument(
        "--title",
        type=str,
        default="Meeting Transcript",
        help="Title for the extracted transcript",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show verbose output during transcription",
    )

    args = parser.parse_args()

    audio_path = Path(args.audio_path)
    if not audio_path.exists():
        print(f"Error: Audio file not found: {audio_path}", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = audio_path.parent / f"{audio_path.stem}_transcript.txt"

    # Create transcriber and run
    transcriber = AudioTranscriber(model_name=args.model, verbose=args.verbose)

    if args.extract:
        result = transcriber.transcribe_with_extraction(
            audio_path=audio_path,
            output_path=output_path,
            stop_at_topic=args.stop_at,
            topic_title=args.title,
        )
    else:
        result = transcriber.transcribe(
            audio_path=audio_path,
            output_path=output_path,
        )

    print(f"\nTranscription complete!")
    print(f"Output: {result.output_path}")


if __name__ == "__main__":
    main()
