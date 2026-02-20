"""Tests for the audio transcription module."""

import pytest


class TestAudioTranscriber:
    """Tests for AudioTranscriber class."""

    def test_import(self):
        """Test that the module can be imported."""
        from elt_doc_transcript_audio import AudioTranscriber

        assert AudioTranscriber is not None

    def test_transcriber_init(self):
        """Test AudioTranscriber initialization."""
        from elt_doc_transcript_audio import AudioTranscriber

        transcriber = AudioTranscriber(model_name="base", verbose=False)
        assert transcriber.model_name == "base"
        assert transcriber.verbose is False

    def test_transcriber_init_default(self):
        """Test AudioTranscriber default initialization."""
        from elt_doc_transcript_audio import AudioTranscriber

        transcriber = AudioTranscriber()
        assert transcriber.model_name == "base"
        assert transcriber.verbose is False
