"""Tests for elt_doc_damabok utils module."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from elt_doc_damabok.utils import (
    build_prompt,
    clear_config_cache,
    embed_query,
    expand_path,
    load_doc_config,
    load_ollama_config,
    load_vector_config,
    _load_json_config,
    _get_config_dir,
)


class TestPathHelpers:
    """Test path helper functions."""

    def test_expand_path_with_tilde(self):
        """Test tilde expansion."""
        result = expand_path("~/test")
        assert "~" not in str(result)
        assert result.is_absolute()

    def test_expand_path_relative(self):
        """Test relative path expansion."""
        result = expand_path("test/path")
        assert result.is_absolute()


class TestConfigLoading:
    """Test configuration loading."""

    def test_load_doc_config(self):
        """Test loading document config."""
        cfg = load_doc_config()
        assert "source_pdf" in cfg
        assert "chunk_size" in cfg
        assert "chunk_overlap" in cfg
        assert "chunking_strategy" in cfg

    def test_load_vector_config(self):
        """Test loading vector config."""
        cfg = load_vector_config()
        assert "embedding_model" in cfg
        assert "llm_model" in cfg
        assert "top_k" in cfg
        assert "max_prompt_chars" in cfg

    def test_load_ollama_config(self):
        """Test loading Ollama config."""
        cfg = load_ollama_config()
        assert "models" in cfg
        assert "system_prompt" in cfg
        assert "test_question" in cfg

    def test_config_caching(self):
        """Test config caching."""
        clear_config_cache()
        
        # First load
        cfg1 = load_doc_config(use_cache=True)
        
        # Second load (should use cache)
        cfg2 = load_doc_config(use_cache=True)
        
        assert cfg1 is cfg2  # Same object from cache

    def test_clear_config_cache(self):
        """Test clearing config cache."""
        clear_config_cache()
        load_doc_config(use_cache=True)
        clear_config_cache()
        # Should not raise


class TestLoadJsonConfig:
    """Test JSON config loading with error handling."""

    def test_load_nonexistent_config(self):
        """Test loading nonexistent config raises error."""
        with pytest.raises(FileNotFoundError):
            _load_json_config("nonexistent_file.json")

    def test_load_invalid_json(self, tmp_path: Path):
        """Test loading invalid JSON raises error."""
        # Create temp config dir with invalid JSON
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        invalid_file = config_dir / "test.json"
        invalid_file.write_text("{ invalid json }")
        
        # Temporarily override _get_config_dir
        import elt_doc_damabok.utils as utils
        original = utils._get_config_dir
        
        def mock_get_config_dir():
            return config_dir
        
        utils._get_config_dir = mock_get_config_dir
        
        try:
            with pytest.raises(RuntimeError, match="Failed to parse JSON"):
                _load_json_config("test.json", use_cache=False)
        finally:
            utils._get_config_dir = original


class TestBuildPrompt:
    """Test prompt building."""

    def test_build_prompt_basic(self):
        """Test basic prompt building."""
        prompt = build_prompt(
            question="What is data governance?",
            contexts=["Context 1", "Context 2"],
            system_prompt="You are a helpful assistant.",
            max_prompt_chars=4000,
        )
        
        assert "You are a helpful assistant." in prompt
        assert "What is data governance?" in prompt
        assert "Excerpt 1:" in prompt
        assert "Excerpt 2:" in prompt
        assert "Answer:" in prompt

    def test_build_prompt_respects_max_chars(self):
        """Test prompt respects max character limit."""
        contexts = ["x" * 1000 for _ in range(20)]
        prompt = build_prompt(
            question="Q",
            contexts=contexts,
            system_prompt="S",
            max_prompt_chars=3000,
        )
        
        assert len(prompt) <= 3000

    def test_build_prompt_empty_contexts(self):
        """Test prompt with empty contexts."""
        prompt = build_prompt(
            question="Q",
            contexts=[],
            system_prompt="S",
            max_prompt_chars=4000,
        )
        
        assert "Question: Q" in prompt
        assert "Excerpt" not in prompt


class TestEmbedQuery:
    """Test query embedding."""

    def test_embed_query_without_ollama(self):
        """Test embedding fails gracefully without Ollama."""
        # This will fail if Ollama is not running, which is expected
        try:
            result = embed_query("test query", model="nomic-embed-text")
            # If successful, check result type
            assert isinstance(result, list)
            assert len(result) > 0
        except RuntimeError as e:
            # Expected if Ollama not available
            assert "Failed to embed" in str(e)


class TestGetConfigDir:
    """Test config directory resolution."""

    def test_get_config_dir_exists(self):
        """Test config directory exists."""
        config_dir = _get_config_dir()
        assert config_dir.exists()
        assert config_dir.is_dir()

    def test_config_files_exist(self):
        """Test config files exist."""
        config_dir = _get_config_dir()
        assert (config_dir / "doc_damabok.json").exists()
        assert (config_dir / "vector_db.json").exists()
        assert (config_dir / "ollama.json").exists()
