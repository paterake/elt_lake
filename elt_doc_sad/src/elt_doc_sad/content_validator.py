"""Content validator for SAD documents."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from docx import Document

from .config_loader import load_sad_template, load_section_guidance


def extract_headings(doc_path: str) -> list[dict[str, Any]]:
    """Extract headings from a Word document.
    
    Args:
        doc_path: Path to the Word document.
        
    Returns:
        List of dictionaries containing heading information.
    """
    doc = Document(doc_path)
    headings = []
    
    for para in doc.paragraphs:
        if para.style.name.startswith('Heading'):
            level = int(para.style.name.split(' ')[-1]) if ' ' in para.style.name else 1
            headings.append({
                "level": level,
                "text": para.text.strip(),
            })
    
    return headings


def validate_sad_structure(doc_path: str) -> dict[str, Any]:
    """Validate SAD document structure against template.
    
    Args:
        doc_path: Path to the SAD document.
        
    Returns:
        Validation result dictionary with status and issues.
    """
    template = load_sad_template()
    headings = extract_headings(doc_path)
    heading_texts = [h["text"] for h in headings]
    
    issues = {
        "missing_required": [],
        "missing_optional": [],
        "found": [],
    }
    
    # Check front matter
    front_matter = template.get("front_matter", [])
    for item in front_matter:
        name = item.get("name", "")
        required = item.get("required", False)
        if name in heading_texts:
            issues["found"].append(f"Front Matter: {name}")
        elif required:
            issues["missing_required"].append(f"Front Matter: {name}")
        else:
            issues["missing_optional"].append(f"Front Matter: {name}")
    
    # Check sections
    sections = template.get("sections", {})
    for section_num, section_data in sections.items():
        section_title = section_data.get("title", "")
        full_title = f"{section_num}. {section_title}"
        
        # Check main section
        if any(full_title in h for h in heading_texts):
            issues["found"].append(full_title)
        else:
            issues["missing_required"].append(full_title)
        
        # Check subsections
        subsections = section_data.get("subsections", {})
        for sub_id, sub_data in subsections.items():
            sub_title = sub_data.get("title", "")
            required = sub_data.get("required", False)
            
            # Format subsection number (e.g., "1.1", "2.3")
            if '.' in sub_id:
                full_sub_id = f"{section_num}.{sub_id.split('.')[1]}"
            else:
                full_sub_id = f"{section_num}.{sub_id}"
            
            full_sub_title = f"{full_sub_id} {sub_title}"
            
            if any(full_sub_title in h for h in heading_texts):
                issues["found"].append(full_sub_title)
            elif required:
                issues["missing_required"].append(full_sub_title)
            else:
                issues["missing_optional"].append(full_sub_title)
    
    return {
        "valid": len(issues["missing_required"]) == 0,
        "issues": issues,
        "completeness": calculate_completeness(issues, template),
    }


def calculate_completeness(issues: dict[str, Any], template: dict[str, Any]) -> float:
    """Calculate document completeness percentage.
    
    Args:
        issues: Issues dictionary from validation.
        template: SAD template structure.
        
    Returns:
        Completeness percentage (0-100).
    """
    total_required = 0
    found_count = len(issues["found"])
    
    # Count front matter
    for item in template.get("front_matter", []):
        if item.get("required", False):
            total_required += 1
    
    # Count sections
    for section_data in template.get("sections", {}).values():
        total_required += 1  # Main section
        for sub_data in section_data.get("subsections", {}).values():
            if sub_data.get("required", False):
                total_required += 1
    
    if total_required == 0:
        return 100.0
    
    return round((found_count / total_required) * 100, 1)


def validate_section_content(doc_path: str, section_id: str) -> dict[str, Any]:
    """Validate content of a specific section.
    
    Args:
        doc_path: Path to the SAD document.
        section_id: Section identifier (e.g., "1.1", "2.3").
        
    Returns:
        Validation result with content assessment.
    """
    from .config_loader import get_section_guidance
    
    doc = Document(doc_path)
    guidance = get_section_guidance(section_id)
    
    if not guidance:
        return {"valid": False, "error": f"No guidance found for section {section_id}"}
    
    # Find section in document
    in_section = False
    section_content = []
    
    for para in doc.paragraphs:
        if para.style.name.startswith('Heading'):
            if section_id in para.text:
                in_section = True
                continue
            elif in_section:
                # Check if this is a subsection or next section
                if para.style.name.split(' ')[-1].isdigit():
                    level = int(para.style.name.split(' ')[-1])
                    if level <= 2:
                        break
        elif in_section and para.text.strip():
            section_content.append(para.text.strip())
    
    content_length = sum(len(c) for c in section_content)
    should_include = guidance.get("should_include", [])
    
    return {
        "valid": content_length > 100,  # At least 100 chars
        "content_length": content_length,
        "paragraphs": len(section_content),
        "should_include_count": len(should_include),
        "guidance": guidance.get("description", ""),
    }


def generate_validation_report(doc_path: str) -> str:
    """Generate a human-readable validation report.
    
    Args:
        doc_path: Path to the SAD document.
        
    Returns:
        Formatted validation report string.
    """
    result = validate_sad_structure(doc_path)
    
    lines = [
        "=" * 60,
        "SAD Document Validation Report",
        "=" * 60,
        f"Document: {doc_path}",
        f"Valid: {'Yes' if result['valid'] else 'No'}",
        f"Completeness: {result['completeness']}%",
        "",
    ]
    
    if result["issues"]["found"]:
        lines.append("Found Sections:")
        for item in result["issues"]["found"]:
            lines.append(f"  ✓ {item}")
        lines.append("")
    
    if result["issues"]["missing_required"]:
        lines.append("Missing Required Sections:")
        for item in result["issues"]["missing_required"]:
            lines.append(f"  ✗ {item}")
        lines.append("")
    
    if result["issues"]["missing_optional"]:
        lines.append("Missing Optional Sections:")
        for item in result["issues"]["missing_optional"]:
            lines.append(f"  ○ {item}")
        lines.append("")
    
    lines.append("=" * 60)
    
    return "\n".join(lines)


def main() -> None:
    """CLI entry point for SAD validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate SAD document")
    parser.add_argument("--input", required=True, help="Input SAD document path")
    parser.add_argument("--section", help="Validate specific section only (e.g., 1.1)")
    parser.add_argument("--report", action="store_true", help="Generate full report")
    
    args = parser.parse_args()
    
    if args.section:
        result = validate_section_content(args.input, args.section)
        print(f"Section {args.section} Validation:")
        for key, value in result.items():
            print(f"  {key}: {value}")
    elif args.report:
        report = generate_validation_report(args.input)
        print(report)
    else:
        result = validate_sad_structure(args.input)
        print(f"Valid: {result['valid']}")
        print(f"Completeness: {result['completeness']}%")
        if result["issues"]["missing_required"]:
            print("\nMissing required sections:")
            for item in result["issues"]["missing_required"]:
                print(f"  - {item}")


if __name__ == "__main__":
    main()
