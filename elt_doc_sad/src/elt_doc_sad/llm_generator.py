"""LLM-based content generation for SAD documents.

This module provides AI-powered content generation using local LLM models
via Ollama. It can generate section content based on integration specifications.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from .config_loader import (
    load_section_guidance,
    load_integration_patterns,
    get_section_guidance,
)

logger = logging.getLogger(__name__)

# Default LLM configuration
DEFAULT_LLM_MODEL = "llama3.1:8b"
DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 2048


class LLMGenerationError(Exception):
    """Exception raised for LLM generation errors."""
    pass


class OllamaNotAvailableError(Exception):
    """Exception raised when Ollama server is not available."""
    pass


def _try_import_ollama() -> Any:
    """Try to import ollama package.
    
    Returns:
        ollama module if available.
        
    Raises:
        LLMGenerationError: If ollama package is not installed.
    """
    try:
        import ollama
        return ollama
    except ImportError:
        logger.error("ollama package not installed")
        raise LLMGenerationError(
            "ollama package not installed. Install with: pip install ollama"
        )


def check_ollama_available() -> bool:
    """Check if Ollama server is available.
    
    Returns:
        True if Ollama server is reachable, False otherwise.
    """
    try:
        ollama = _try_import_ollama()
        ollama.list()
        logger.debug("Ollama server is available")
        return True
    except (LLMGenerationError, Exception) as e:
        logger.debug("Ollama server not available: %s", e)
        return False


def check_model_available(model_name: str) -> bool:
    """Check if a specific model is available in Ollama.
    
    Args:
        model_name: Name of the model to check.
        
    Returns:
        True if model is available, False otherwise.
    """
    try:
        ollama = _try_import_ollama()
        listed = ollama.list()
        installed_models = {m.model for m in listed.models}
        
        # Check with and without :latest suffix
        model_variants = [model_name, f"{model_name}:latest"]
        for variant in model_variants:
            if variant in installed_models or model_name in variant:
                logger.debug("Model available: %s", model_name)
                return True
        
        logger.debug("Model not available: %s", model_name)
        return False
        
    except (LLMGenerationError, Exception) as e:
        logger.warning("Failed to check model availability: %s", e)
        return False


def build_section_prompt(
    section_id: str,
    integration_spec: dict[str, Any],
) -> str:
    """Build a prompt for generating section content.
    
    Args:
        section_id: Section identifier (e.g., "1.1", "2.3").
        integration_spec: Integration specification dictionary.
        
    Returns:
        Formatted prompt string.
    """
    guidance = get_section_guidance(section_id)
    
    if not guidance:
        logger.warning("No guidance found for section %s", section_id)
        return ""
    
    # Extract guidance components
    description = guidance.get("description", "")
    should_include = guidance.get("should_include", [])
    example_topics = guidance.get("example_topics", [])
    
    # Build prompt
    prompt_parts = [
        f"You are a technical writer creating a Solution Architecture Definition (SAD) document.",
        f"",
        f"Generate content for section {section_id}: {guidance.get('title', '')}",
        f"",
        f"Section description: {description}",
        f"",
        f"This section should include:",
    ]
    
    for item in should_include:
        prompt_parts.append(f"- {item}")
    
    prompt_parts.extend([
        f"",
        f"Integration Details:",
        f"- Integration ID: {integration_spec.get('integration_id', 'TBD')}",
        f"- Vendor: {integration_spec.get('vendor_name', 'TBD')}",
        f"- Pattern: {integration_spec.get('pattern', 'TBD')}",
        f"- Data Flow: {integration_spec.get('data_flow', 'TBD')}",
        f"",
        f"Example topics that might be covered:",
    ])
    
    for topic in example_topics[:5]:  # Limit to 5 examples
        prompt_parts.append(f"- {topic}")
    
    prompt_parts.extend([
        f"",
        f"Requirements:",
        f"- Write in professional technical English",
        f"- Use bullet points where appropriate",
        f"- Be specific to the integration details provided",
        f"- Include relevant technical details (protocols, security, etc.)",
        f"- Keep content concise but comprehensive",
        f"- Do not include section headers or titles",
        f"",
        f"Generate the section content:",
    ])
    
    return "\n".join(prompt_parts)


def generate_section_content(
    section_id: str,
    integration_spec: dict[str, Any],
    model: str = DEFAULT_LLM_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> str:
    """Generate content for a SAD section using LLM.
    
    Args:
        section_id: Section identifier (e.g., "1.1", "2.3").
        integration_spec: Integration specification dictionary.
        model: LLM model to use (default: llama3.1:8b).
        temperature: Sampling temperature (default: 0.7).
        max_tokens: Maximum tokens to generate (default: 2048).
        
    Returns:
        Generated section content.
        
    Raises:
        LLMGenerationError: If content generation fails.
        OllamaNotAvailableError: If Ollama server is not available.
    """
    logger.info(
        "Generating content for section %s using model %s",
        section_id,
        model,
    )
    
    # Check Ollama availability
    if not check_ollama_available():
        raise OllamaNotAvailableError(
            "Ollama server is not available. Ensure 'ollama serve' is running."
        )
    
    # Check model availability
    if not check_model_available(model):
        logger.warning("Model %s not available, attempting to pull...", model)
        try:
            ollama = _try_import_ollama()
            for _ in ollama.pull(model=model):
                pass
            logger.info("Model pulled successfully: %s", model)
        except Exception as e:
            raise LLMGenerationError(f"Failed to pull model {model}: {e}")
    
    # Build prompt
    prompt = build_section_prompt(section_id, integration_spec)
    
    if not prompt:
        raise LLMGenerationError(f"Failed to build prompt for section {section_id}")
    
    # Generate content
    try:
        ollama = _try_import_ollama()
        
        logger.debug("Sending request to Ollama...")
        response = ollama.generate(
            model=model,
            prompt=prompt,
            options={
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        )
        
        content = response.get("response", "")
        
        if not content.strip():
            raise LLMGenerationError("LLM returned empty content")
        
        logger.info(
            "Generated %d characters for section %s",
            len(content),
            section_id,
        )
        
        return content
        
    except Exception as e:
        logger.exception("LLM generation failed")
        raise LLMGenerationError(f"Failed to generate content: {e}")


def generate_full_sad_content(
    integration_spec: dict[str, Any],
    model: str = DEFAULT_LLM_MODEL,
    sections: list[str] | None = None,
) -> dict[str, str]:
    """Generate content for multiple SAD sections.
    
    Args:
        integration_spec: Integration specification dictionary.
        model: LLM model to use.
        sections: List of section IDs to generate (default: all sections).
        
    Returns:
        Dictionary mapping section IDs to generated content.
        
    Raises:
        LLMGenerationError: If content generation fails.
    """
    if sections is None:
        # Generate all sections
        sections = [
            "1.1", "1.2", "1.3", "1.4", "1.5",
            "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7",
            "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7",
            "4.1", "4.2", "4.3", "4.4",
            "5.1", "5.2", "5.3",
            "6.1", "6.2", "6.3",
            "7.1", "7.2", "7.3",
        ]
    
    results = {}
    failed = []
    
    for section_id in sections:
        try:
            content = generate_section_content(section_id, integration_spec, model)
            results[section_id] = content
        except (LLMGenerationError, OllamaNotAvailableError) as e:
            logger.warning("Failed to generate section %s: %s", section_id, e)
            failed.append(section_id)
    
    if failed:
        logger.warning("Failed to generate %d sections: %s", len(failed), failed)
    
    logger.info(
        "Generated content for %d/%d sections",
        len(results),
        len(sections),
    )
    
    return results


def create_integration_spec(
    integration_id: str,
    vendor_name: str,
    pattern: str,
    description: str = "",
    data_elements: list[str] | None = None,
    security_requirements: list[str] | None = None,
) -> dict[str, Any]:
    """Create an integration specification for LLM generation.
    
    Args:
        integration_id: Integration identifier.
        vendor_name: Vendor company name.
        pattern: Integration pattern ID.
        description: Brief description of the integration.
        data_elements: List of data elements being transferred.
        security_requirements: List of security requirements.
        
    Returns:
        Integration specification dictionary.
    """
    patterns = load_integration_patterns()
    pattern_data = patterns.get("patterns", {}).get(pattern, {})
    
    spec = {
        "integration_id": integration_id,
        "vendor_name": vendor_name,
        "pattern": pattern,
        "pattern_name": pattern_data.get("name", pattern),
        "data_flow": pattern_data.get("diagram", ""),
        "description": description,
        "data_elements": data_elements or [],
        "security_requirements": security_requirements or [],
        "components": pattern_data.get("components", []),
    }
    
    logger.debug("Created integration spec: %s", integration_id)
    return spec


def save_generated_content(
    content: dict[str, str],
    output_dir: str,
    integration_id: str,
) -> Path:
    """Save generated content to JSON files.
    
    Args:
        content: Dictionary mapping section IDs to content.
        output_dir: Output directory.
        integration_id: Integration identifier.
        
    Returns:
        Path to the output directory.
    """
    output_path = Path(output_dir).expanduser().resolve()
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save all content to single file
    combined_file = output_path / f"{integration_id}_generated_content.json"
    with combined_file.open("w", encoding="utf-8") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
    
    logger.info("Saved generated content to: %s", combined_file)
    
    # Save individual section files
    for section_id, section_content in content.items():
        section_file = output_path / f"{integration_id}_section_{section_id}.txt"
        with section_file.open("w", encoding="utf-8") as f:
            f.write(section_content)
    
    logger.debug("Saved %d individual section files", len(content))
    
    return output_path


def main() -> None:
    """CLI entry point for LLM content generation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate SAD content using LLM")
    parser.add_argument(
        "--integration-id",
        required=True,
        help="Integration ID (e.g., INT001)",
    )
    parser.add_argument(
        "--vendor-name",
        required=True,
        help="Vendor name",
    )
    parser.add_argument(
        "--pattern",
        required=True,
        help="Integration pattern (e.g., outbound_eib_sftp)",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output directory for generated content",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_LLM_MODEL,
        help=f"LLM model to use (default: {DEFAULT_LLM_MODEL})",
    )
    parser.add_argument(
        "--sections",
        nargs="+",
        help="Specific sections to generate (default: all)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check Ollama availability and exit",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    if args.check:
        if check_ollama_available():
            print("✓ Ollama server is available")
            if check_model_available(args.model):
                print(f"✓ Model {args.model} is available")
            else:
                print(f"✗ Model {args.model} is not available")
        else:
            print("✗ Ollama server is not available")
            raise SystemExit(1)
        return
    
    try:
        # Create integration spec
        spec = create_integration_spec(
            integration_id=args.integration_id,
            vendor_name=args.vendor_name,
            pattern=args.pattern,
        )
        
        # Generate content
        content = generate_full_sad_content(
            integration_spec=spec,
            model=args.model,
            sections=args.sections,
        )
        
        # Save content
        output_path = save_generated_content(
            content=content,
            output_dir=args.output_dir,
            integration_id=args.integration_id,
        )
        
        print(f"Generated content for {len(content)} sections")
        print(f"Output directory: {output_path}")
        
    except OllamaNotAvailableError as e:
        print(f"Ollama not available: {e}")
        raise SystemExit(1)
    except LLMGenerationError as e:
        print(f"Generation error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
