"""SAD document generator."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

from .config_loader import load_sad_template, load_section_guidance


def _get_resources_dir() -> Path:
    """Get the resources directory path."""
    return Path(__file__).resolve().parent.parent.parent / "resources"


def _expand_path(path_str: str) -> Path:
    """Expand user path and resolve to absolute path."""
    return Path(os.path.expanduser(path_str)).resolve()


def create_cover_page(doc: Document, title: str, integration_id: str, vendor_name: str) -> None:
    """Create a cover page for the SAD document.
    
    Args:
        doc: Word document to add cover page to.
        title: Document title.
        integration_id: Integration identifier (e.g., INT001).
        vendor_name: Vendor company name.
    """
    # Add title
    heading = doc.add_heading(level=1)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = heading.add_run(title)
    run.font.size = Pt(24)
    run.font.bold = True
    
    # Add subtitle
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle_run = subtitle.add_run(f"Solution Architecture Definition")
    subtitle_run.font.size = Pt(16)
    
    # Add integration details
    details = doc.add_paragraph()
    details.alignment = WD_ALIGN_PARAGRAPH.CENTER
    details.add_run(f"\nIntegration ID: {integration_id}\n")
    details.add_run(f"Vendor: {vendor_name}\n")
    details.add_run(f"Version: 1.0\n")
    
    # Add cover image if available
    resources_dir = _get_resources_dir()
    cover_image = resources_dir / "cover_image.jpeg"
    if cover_image.exists():
        doc.add_picture(str(cover_image), width=Inches(3))
        # Center the image
        for paragraph in doc.paragraphs:
            if paragraph.runs and paragraph.runs[-1].text == '':
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER


def create_document_history(doc: Document) -> None:
    """Create the document history table.
    
    Args:
        doc: Word document to add table to.
    """
    doc.add_heading("Document History", level=2)
    table = doc.add_table(rows=2, cols=4)
    table.style = 'Table Grid'
    
    # Header row
    headers = ["Version", "Date", "Author", "Changes"]
    for i, header in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = header
        cell.paragraphs[0].runs[0].font.bold = True
    
    # First data row (initial version)
    row = table.rows[1]
    row.cells[0].text = "1.0"
    row.cells[1].text = "[Date]"
    row.cells[2].text = "[Author]"
    row.cells[3].text = "Initial version"


def create_document_review(doc: Document) -> None:
    """Create the document review table.
    
    Args:
        doc: Word document to add table to.
    """
    doc.add_heading("Document Review", level=2)
    table = doc.add_table(rows=2, cols=4)
    table.style = 'Table Grid'
    
    # Header row
    headers = ["Name", "Role", "Date", "Signature"]
    for i, header in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = header
        cell.paragraphs[0].runs[0].font.bold = True


def create_approvals(doc: Document) -> None:
    """Create the approvals table.
    
    Args:
        doc: Word document to add table to.
    """
    doc.add_heading("Approvals", level=2)
    table = doc.add_table(rows=2, cols=4)
    table.style = 'Table Grid'
    
    # Header row
    headers = ["Name", "Role", "Date", "Signature"]
    for i, header in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = header
        cell.paragraphs[0].runs[0].font.bold = True


def create_section_placeholder(doc: Document, section_num: str, section_id: str, section_data: dict[str, Any]) -> None:
    """Create a section with placeholder content.
    
    Args:
        doc: Word document to add section to.
        section_num: Section number (e.g., "1", "2").
        section_id: Subsection ID (e.g., "1", "1.1", "2.3").
        section_data: Section configuration data.
    """
    title = section_data.get("title", f"Section {section_id}")
    level = int(section_data.get("level", 2))
    
    # Create full heading with number
    if section_id == section_num:
        heading_text = f"{section_num}. {title}"
    else:
        heading_text = f"{section_id} {title}"
    
    heading = doc.add_heading(heading_text, level=level)
    
    # Add guidance as placeholder
    guidance = load_section_guidance()
    section_key = f"{section_id}"
    
    # Find matching guidance
    guidance_key = None
    for key in guidance:
        if key.startswith(section_id):
            guidance_key = key
            break
    
    if guidance_key and guidance_key in guidance:
        guidance_data = guidance[guidance_key]
        description = guidance_data.get("description", "")
        should_include = guidance_data.get("should_include", [])
        
        if description:
            doc.add_paragraph(f"[{description}]")
        
        if should_include:
            doc.add_paragraph("This section should include:")
            for item in should_include:
                doc.add_paragraph(f"  • {item}", style="List Bullet")


def generate_sad_document(
    output_path: str,
    integration_id: str,
    vendor_name: str,
    title: str | None = None,
) -> Path:
    """Generate a complete SAD document.
    
    Args:
        output_path: Path to save the document (directory or full file path).
        integration_id: Integration identifier (e.g., INT001).
        vendor_name: Vendor company name.
        title: Optional custom title. Defaults to standard SAD title.
        
    Returns:
        Path to the generated document.
    """
    doc = Document()
    
    # Set default title
    if title is None:
        title = f"SAD_{integration_id}_{vendor_name.replace(' ', '_')}_V1_0"
    
    # Create cover page
    create_cover_page(doc, title, integration_id, vendor_name)
    
    # Add page break
    doc.add_page_break()
    
    # Front matter
    create_document_history(doc)
    doc.add_paragraph()
    create_document_review(doc)
    doc.add_paragraph()
    create_approvals(doc)
    
    # Load template structure
    template = load_sad_template()
    
    # Generate sections
    for section_num, section_data in template.get("sections", {}).items():
        doc.add_page_break()
        
        # Main section heading
        section_title = section_data.get("title", f"Section {section_num}")
        doc.add_heading(f"{section_num}. {section_title}", level=1)
        
        # Subsections
        subsections = section_data.get("subsections", {})
        for sub_id, sub_data in subsections.items():
            full_id = f"{section_num}.{sub_id.split('.')[1]}" if '.' in sub_id else sub_id
            create_section_placeholder(doc, section_num, full_id, sub_data)
    
    # Determine output path
    output = _expand_path(output_path)
    if output.is_dir():
        output = output / f"{title}.docx"
    elif not output.suffix:
        output = output / f"{title}.docx"
    
    # Ensure parent directory exists
    output.parent.mkdir(parents=True, exist_ok=True)
    
    # Save document
    doc.save(str(output))
    
    return output


def main() -> None:
    """CLI entry point for SAD generation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate SAD document")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--integration-id", required=True, help="Integration ID (e.g., INT001)")
    parser.add_argument("--vendor-name", required=True, help="Vendor name")
    parser.add_argument("--title", help="Custom title (optional)")
    
    args = parser.parse_args()
    
    output_path = generate_sad_document(
        output_path=args.output_dir,
        integration_id=args.integration_id,
        vendor_name=args.vendor_name,
        title=args.title,
    )
    
    print(f"SAD document generated: {output_path}")


if __name__ == "__main__":
    main()
