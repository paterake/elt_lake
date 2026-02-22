"""SAD pipeline helper for automated workflows."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .config_loader import load_sad_template, load_section_guidance, load_integration_patterns
from .sad_generator import generate_sad_document


def _expand_path(path_str: str) -> Path:
    """Expand user path and resolve to absolute path."""
    return Path(os.path.expanduser(path_str)).resolve()


def build_sad_prompt(
    integration_id: str,
    vendor_name: str,
    pattern_id: str | None = None,
) -> dict[str, Any]:
    """Build a prompt for generating SAD content.
    
    Args:
        integration_id: Integration identifier.
        vendor_name: Vendor name.
        pattern_id: Optional integration pattern ID.
        
    Returns:
        Dictionary containing prompt structure and guidance.
    """
    template = load_sad_template()
    guidance = load_section_guidance()
    patterns = load_integration_patterns()
    
    prompt = {
        "integration_id": integration_id,
        "vendor_name": vendor_name,
        "pattern": None,
        "sections": {},
    }
    
    # Add pattern info if specified
    if pattern_id:
        pattern = patterns.get("patterns", {}).get(pattern_id)
        if pattern:
            prompt["pattern"] = pattern
    
    # Add section guidance
    for section_num, section_data in template.get("sections", {}).items():
        section_key = section_data.get("title", "")
        prompt["sections"][section_num] = {
            "title": section_key,
            "guidance": {},
        }
        
        for sub_id, sub_data in section_data.get("subsections", {}).items():
            sub_title = sub_data.get("title", "")
            sub_guidance = guidance.get(f"{section_num}.{sub_id.split('.')[1]}", {})
            prompt["sections"][section_num]["guidance"][sub_title] = sub_guidance
    
    return prompt


def export_prompt_to_file(
    output_dir: str,
    integration_id: str,
    vendor_name: str,
    pattern_id: str | None = None,
) -> Path:
    """Export SAD generation prompt to a file.
    
    Args:
        output_dir: Output directory.
        integration_id: Integration identifier.
        vendor_name: Vendor name.
        pattern_id: Optional integration pattern ID.
        
    Returns:
        Path to the exported prompt file.
    """
    prompt = build_sad_prompt(integration_id, vendor_name, pattern_id)
    
    output_path = _expand_path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    prompt_file = output_path / f"{integration_id}_{vendor_name.replace(' ', '_')}_prompt.json"
    
    with prompt_file.open("w") as f:
        json.dump(prompt, f, indent=2)
    
    return prompt_file


def create_sad_from_spec(
    spec_path: str,
    output_dir: str,
) -> Path:
    """Generate SAD document from a specification file.
    
    Args:
        spec_path: Path to JSON specification file.
        output_dir: Output directory for the SAD document.
        
    Returns:
        Path to the generated SAD document.
    """
    spec_path = _expand_path(spec_path)
    
    with spec_path.open() as f:
        spec = json.load(f)
    
    integration_id = spec.get("integration_id", "INT000")
    vendor_name = spec.get("vendor_name", "Unknown Vendor")
    title = spec.get("title")
    
    output_path = generate_sad_document(
        output_path=output_dir,
        integration_id=integration_id,
        vendor_name=vendor_name,
        title=title,
    )
    
    return output_path


def main() -> None:
    """CLI entry point for SAD pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description="SAD pipeline helper")
    parser.add_argument("command", choices=["prompt", "generate"], help="Command to run")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--integration-id", help="Integration ID")
    parser.add_argument("--vendor-name", help="Vendor name")
    parser.add_argument("--pattern", help="Integration pattern ID")
    parser.add_argument("--spec", help="Specification file path (for generate command)")
    
    args = parser.parse_args()
    
    if args.command == "prompt":
        if not args.integration_id or not args.vendor_name:
            parser.error("prompt command requires --integration-id and --vendor-name")
        
        prompt_path = export_prompt_to_file(
            output_dir=args.output_dir,
            integration_id=args.integration_id,
            vendor_name=args.vendor_name,
            pattern_id=args.pattern,
        )
        print(f"Prompt exported to: {prompt_path}")
        
    elif args.command == "generate":
        if not args.spec:
            parser.error("generate command requires --spec")
        
        output_path = create_sad_from_spec(
            spec_path=args.spec,
            output_dir=args.output_dir,
        )
        print(f"SAD document generated: {output_path}")


if __name__ == "__main__":
    main()
