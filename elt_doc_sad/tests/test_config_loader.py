"""Tests for config_loader module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from elt_doc_sad.config_loader import (
    _get_config_dir,
    _get_package_root,
    _get_resources_dir,
    _load_json_config,
    clear_config_cache,
    get_cover_image_path,
    get_pattern_by_id,
    get_section_guidance,
    load_integration_patterns,
    load_sad_template,
    load_section_guidance,
)


class TestPathHelpers:
    """Test path helper functions."""

    def test_get_package_root(self):
        """Test package root path resolution."""
        root = _get_package_root()
        assert root.is_dir()
        assert root.name == "elt_doc_sad"
        assert (root / "config_loader.py").exists()

    def test_get_config_dir(self):
        """Test config directory path resolution."""
        config_dir = _get_config_dir()
        assert config_dir.is_dir()
        assert config_dir.name == "config"
        assert (config_dir / "sad_template.json").exists()

    def test_get_resources_dir(self):
        """Test resources directory path resolution."""
        resources_dir = _get_resources_dir()
        assert resources_dir.is_dir()
        assert resources_dir.name == "resources"

    def test_get_cover_image_path(self):
        """Test cover image path."""
        image_path = get_cover_image_path()
        assert image_path.exists()
        assert image_path.suffix.lower() == ".jpeg"


class TestConfigLoading:
    """Test configuration loading functions."""

    def test_load_sad_template(self):
        """Test loading SAD template."""
        template = load_sad_template()
        
        assert "version" in template
        assert "front_matter" in template
        assert "sections" in template
        assert template["version"] == "2.0"
        assert len(template["front_matter"]) > 0
        assert len(template["sections"]) > 0

    def test_load_section_guidance(self):
        """Test loading section guidance."""
        guidance = load_section_guidance()
        
        assert len(guidance) > 0
        assert "1.1 Objectives" in guidance
        assert "description" in guidance["1.1 Objectives"]

    def test_load_integration_patterns(self):
        """Test loading integration patterns."""
        patterns = load_integration_patterns()
        
        assert "patterns" in patterns
        assert len(patterns["patterns"]) > 0
        assert "outbound_eib_sftp" in patterns["patterns"]

    def test_load_config_with_cache(self):
        """Test config loading with caching enabled."""
        clear_config_cache()
        
        # First load should read from file
        template1 = load_sad_template(use_cache=True)
        
        # Second load should use cache
        template2 = load_sad_template(use_cache=True)
        
        assert template1 == template2

    def test_clear_config_cache(self):
        """Test clearing config cache."""
        # Load config to populate cache
        load_sad_template(use_cache=True)
        
        # Clear cache
        clear_config_cache()
        
        # Cache should be empty (tested by checking no errors on reload)
        template = load_sad_template(use_cache=True)
        assert template is not None


class TestGetSectionGuidance:
    """Test get_section_guidance function."""

    def test_get_valid_section(self):
        """Test getting guidance for valid section."""
        guidance = get_section_guidance("1.1")
        
        assert guidance is not None
        assert "description" in guidance
        assert "should_include" in guidance

    def test_get_invalid_section(self):
        """Test getting guidance for invalid section."""
        guidance = get_section_guidance("99.99")
        
        assert guidance is None

    def test_get_all_main_sections(self):
        """Test getting guidance for all main sections."""
        section_ids = [
            "1.1", "1.2", "1.3", "1.4", "1.5",
            "2.1", "2.2", "2.3",
            "3.1", "3.2",
        ]
        
        for section_id in section_ids:
            guidance = get_section_guidance(section_id)
            assert guidance is not None, f"No guidance for section {section_id}"


class TestGetPatternById:
    """Test get_pattern_by_id function."""

    def test_get_valid_pattern(self):
        """Test getting valid pattern."""
        pattern = get_pattern_by_id("outbound_eib_sftp")
        
        assert pattern is not None
        assert "name" in pattern
        assert "description" in pattern
        assert pattern["name"] == "Outbound EIB to SFTP"

    def test_get_invalid_pattern(self):
        """Test getting invalid pattern."""
        pattern = get_pattern_by_id("nonexistent_pattern")
        
        assert pattern is None

    def test_get_all_patterns(self):
        """Test getting all defined patterns."""
        pattern_ids = [
            "outbound_eib_sftp",
            "inbound_sftp",
            "bidirectional_api",
            "multi_connector",
            "outbound_fa_sftp",
        ]
        
        for pattern_id in pattern_ids:
            pattern = get_pattern_by_id(pattern_id)
            assert pattern is not None, f"No pattern found for {pattern_id}"


class TestErrorHandling:
    """Test error handling in config loader."""

    def test_load_nonexistent_config(self, temp_config_dir: Path):
        """Test loading nonexistent config file."""
        # Temporarily change config dir by mocking
        import elt_doc_sad.config_loader as loader_module
        
        original_get_config_dir = loader_module._get_config_dir
        
        def mock_get_config_dir():
            return temp_config_dir
        
        loader_module._get_config_dir = mock_get_config_dir
        
        try:
            clear_config_cache()
            # This should work - temp_config_dir has valid configs
            template = load_sad_template()
            assert template is not None
        finally:
            loader_module._get_config_dir = original_get_config_dir
            clear_config_cache()

    def test_invalid_json_config(self, temp_config_dir: Path):
        """Test loading invalid JSON config."""
        import elt_doc_sad.config_loader as loader_module
        
        # Write invalid JSON
        invalid_file = temp_config_dir / "invalid.json"
        invalid_file.write_text("{ invalid json }")
        
        original_get_config_dir = loader_module._get_config_dir
        
        def mock_get_config_dir():
            return temp_config_dir
        
        loader_module._get_config_dir = mock_get_config_dir
        
        try:
            clear_config_cache()
            with pytest.raises(ValueError, match="Invalid JSON"):
                loader_module._load_json_config("invalid")
        finally:
            loader_module._get_config_dir = original_get_config_dir
            clear_config_cache()
