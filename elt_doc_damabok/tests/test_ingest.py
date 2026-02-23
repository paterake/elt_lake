"""Tests for elt_doc_damabok ingest module."""

from __future__ import annotations

from pathlib import Path

import pytest


class TestChunkPages:
    """Test text chunking."""

    def test_chunk_pages_basic(self):
        """Test basic chunking."""
        from elt_doc_damabok.text_processor import _chunk_pages
        
        pages = ["x" * 2000]  # 2000 character page
        chunks = _chunk_pages(pages, max_chars=1000, overlap=200)
        
        assert len(chunks) > 1
        # First chunk should be 1000 chars
        assert len(chunks[0]) == 1000
        # Should have overlap
        assert "x" * 200 in chunks[0] and "x" * 200 in chunks[1]

    def test_chunk_pages_overlap_less_than_size(self):
        """Test that overlap must be less than size."""
        from elt_doc_damabok.text_processor import _chunk_pages
        
        with pytest.raises(ValueError, match="must be less than"):
            _chunk_pages(["test"], max_chars=100, overlap=100)

    def test_chunk_pages_empty_page(self):
        """Test chunking with empty page."""
        from elt_doc_damabok.text_processor import _chunk_pages
        
        pages = ["", "content", ""]
        chunks = _chunk_pages(pages, max_chars=100, overlap=20)
        
        # Empty pages should be skipped
        assert len(chunks) == 1
        assert chunks[0] == "content"

    def test_chunk_pages_small_text(self):
        """Test chunking text smaller than chunk size."""
        from elt_doc_damabok.text_processor import _chunk_pages
        
        pages = ["small text"]
        chunks = _chunk_pages(pages, max_chars=1000, overlap=200)
        
        assert len(chunks) == 1
        assert chunks[0] == "small text"


class TestExtractPages:
    """Test PDF text extraction."""

    def test_extract_pages_nonexistent_file(self):
        """Test extraction of nonexistent file raises error."""
        from elt_doc_damabok.text_processor import _extract_pages
        
        nonexistent = Path("/nonexistent/file.pdf")
        with pytest.raises(FileNotFoundError):
            _extract_pages(nonexistent)


# Tests that require chromadb are skipped due to Python 3.14 compatibility issues
# Run these manually with an older Python version if needed

@pytest.mark.skip(reason="Requires chromadb which has Python 3.14 compatibility issues")
class TestEmbedTexts:
    """Test text embedding."""

    def test_embed_texts_empty(self):
        """Test embedding empty list."""
        from elt_doc_damabok.ingest import _embed_texts
        
        embeddings = _embed_texts([], model="nomic-embed-text")
        assert embeddings == []

    def test_embed_texts_without_ollama(self):
        """Test embedding fails gracefully without Ollama."""
        from elt_doc_damabok.ingest import _embed_texts
        
        try:
            result = _embed_texts(["test"], model="nomic-embed-text")
            # If successful, check result structure
            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], list)
        except RuntimeError as e:
            # Expected if Ollama not available
            assert "Failed to embed" in str(e)


@pytest.mark.skip(reason="Requires chromadb which has Python 3.14 compatibility issues")
class TestBuildIndex:
    """Test index building."""

    def test_build_index_config_error(self, monkeypatch):
        """Test build index handles config errors."""
        from elt_doc_damabok import utils
        from elt_doc_damabok.ingest import build_index
        
        # Mock load_doc_config to raise error
        def mock_load(*args, **kwargs):
            raise FileNotFoundError("Config not found")
        
        monkeypatch.setattr(utils, "load_doc_config", mock_load)
        
        with pytest.raises(FileNotFoundError):
            build_index()


@pytest.mark.skip(reason="Requires chromadb which has Python 3.14 compatibility issues")
class TestIntegration:
    """Integration tests for ingest pipeline."""

    def test_chunk_then_embed(self):
        """Test chunking followed by embedding."""
        from elt_doc_damabok.ingest import _embed_texts
        from elt_doc_damabok.text_processor import _chunk_pages
        
        pages = ["This is a test page with some content."]
        chunks = _chunk_pages(pages, max_chars=100, overlap=20)
        
        assert len(chunks) > 0
        
        # Try embedding (will fail without Ollama, which is OK)
        try:
            embeddings = _embed_texts(chunks, model="nomic-embed-text")
            assert len(embeddings) == len(chunks)
        except RuntimeError:
            # Expected without Ollama
            pass
