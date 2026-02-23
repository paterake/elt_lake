"""Tests for llm_generator module."""

from __future__ import annotations

import pytest

from elt_doc_sad.llm_generator import (
    LLMGenerationError,
    OllamaNotAvailableError,
    build_section_prompt,
    check_model_available,
    check_ollama_available,
    create_integration_spec,
    generate_section_content,
)


class TestOllamaAvailability:
    """Test Ollama availability checks."""

    def test_check_ollama_available(self):
        """Test checking Ollama server availability."""
        # This will return False if Ollama is not running
        # which is expected in test environments
        result = check_ollama_available()
        assert isinstance(result, bool)

    def test_check_model_available(self):
        """Test checking model availability."""
        # Test with a common model name
        result = check_model_available("llama3.1:8b")
        assert isinstance(result, bool)

    def test_check_nonexistent_model(self):
        """Test checking nonexistent model."""
        result = check_model_available("nonexistent_model_xyz123")
        assert result is False


class TestBuildSectionPrompt:
    """Test prompt building for LLM generation."""

    def test_build_prompt_valid_section(self, fictional_integration: dict):
        """Test building prompt for valid section."""
        prompt = build_section_prompt("1.1", fictional_integration)
        
        assert len(prompt) > 0
        assert "1.1" in prompt
        # Section title comes from guidance, not the prompt itself
        assert fictional_integration["integration_id"] in prompt
        assert fictional_integration["vendor_name"] in prompt
        assert "Primary objectives" in prompt  # From description

    def test_build_prompt_invalid_section(self, fictional_integration: dict):
        """Test building prompt for invalid section."""
        prompt = build_section_prompt("99.99", fictional_integration)
        
        # Should return empty string for unknown sections
        assert prompt == ""

    def test_build_prompt_includes_requirements(self, fictional_integration: dict):
        """Test that prompt includes requirements."""
        prompt = build_section_prompt("1.1", fictional_integration)
        
        assert "Requirements:" in prompt
        assert "professional technical English" in prompt
        assert "bullet points" in prompt


class TestCreateIntegrationSpec:
    """Test integration spec creation."""

    def test_create_basic_spec(self):
        """Test creating basic integration spec."""
        spec = create_integration_spec(
            integration_id="TEST001",
            vendor_name="Test Vendor",
            pattern="outbound_eib_sftp",
        )
        
        assert spec["integration_id"] == "TEST001"
        assert spec["vendor_name"] == "Test Vendor"
        assert spec["pattern"] == "outbound_eib_sftp"
        assert "data_flow" in spec
        assert "components" in spec

    def test_create_spec_with_details(self):
        """Test creating spec with additional details."""
        spec = create_integration_spec(
            integration_id="TEST002",
            vendor_name="Test Vendor 2",
            pattern="bidirectional_api",
            description="Test integration description",
            data_elements=["Field1", "Field2"],
            security_requirements=["OAuth 2.0", "TLS 1.2+"],
        )
        
        assert spec["description"] == "Test integration description"
        assert spec["data_elements"] == ["Field1", "Field2"]
        assert spec["security_requirements"] == ["OAuth 2.0", "TLS 1.2+"]

    def test_create_spec_invalid_pattern(self):
        """Test creating spec with invalid pattern."""
        spec = create_integration_spec(
            integration_id="TEST003",
            vendor_name="Test Vendor 3",
            pattern="nonexistent_pattern",
        )
        
        # Should still create spec but with empty pattern data
        assert spec["integration_id"] == "TEST003"
        assert spec["pattern_name"] == "nonexistent_pattern"


class TestGenerateSectionContent:
    """Test LLM content generation."""

    def test_generate_without_ollama(self, fictional_integration: dict):
        """Test generation fails gracefully without Ollama."""
        if not check_ollama_available():
            with pytest.raises(OllamaNotAvailableError):
                generate_section_content("1.1", fictional_integration)

    def test_generate_invalid_section(self, fictional_integration: dict):
        """Test generation fails for invalid section."""
        # Even with Ollama, invalid section should fail
        if check_ollama_available():
            with pytest.raises(LLMGenerationError):
                generate_section_content("99.99", fictional_integration)


class TestSaveGeneratedContent:
    """Test saving generated content."""

    def test_save_content_to_json(
        self,
        temp_output_dir,
        fictional_integration: dict,
    ):
        """Test saving generated content to JSON."""
        from elt_doc_sad.llm_generator import save_generated_content
        
        content = {
            "1.1": "Objectives content here",
            "1.2": "Functionality content here",
        }
        
        output_path = save_generated_content(
            content=content,
            output_dir=str(temp_output_dir),
            integration_id=fictional_integration["integration_id"],
        )
        
        assert output_path.exists()
        
        # Check combined file
        combined_file = output_path / f"{fictional_integration['integration_id']}_generated_content.json"
        assert combined_file.exists()
        
        # Check individual files
        section_file = output_path / f"{fictional_integration['integration_id']}_section_1.1.txt"
        assert section_file.exists()
