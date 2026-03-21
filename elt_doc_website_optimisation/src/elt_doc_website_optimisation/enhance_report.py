"""LLM-based report enhancement for client-facing output."""

import json
from pathlib import Path
from typing import Any

from docx import Document


def extract_assessment_data(doc_path: Path) -> dict[str, Any]:
    """Extract structured data from Python-generated assessment document."""
    doc = Document(doc_path)
    
    data = {
        "assessment_name": "",
        "date": "",
        "websites": [],
        "credentials_used": {
            "wordpress_admin": False,
            "google_analytics": False
        },
        "raw_findings": []
    }
    
    current_section = None
    current_website = None
    current_finding_section = None
    
    for para in doc.paragraphs:
        text = para.text.strip()
        style = para.style.name
        
        # Extract assessment name
        if style == "Title" and text:
            data["assessment_name"] = text
        
        # Extract date
        if "Generated:" in text:
            data["date"] = text.replace("Generated:", "").strip()
        
        # Detect website sections
        if style == "Heading 1" and "Website to assess" in text:
            current_website = {
                "name": text,
                "url": "",
                "score": 0.0,
                "sections": {}
            }
            data["websites"].append(current_website)
        
        # Extract URL
        if text.startswith("URL:"):
            if current_website:
                current_website["url"] = text.replace("URL:", "").strip()
        
        # Extract score
        if "Overall Score:" in text:
            if current_website:
                score_text = text.split("Overall Score:")[1].strip()
                try:
                    current_website["score"] = float(score_text.split("/")[0])
                except ValueError:
                    pass
        
        # Detect section headings
        if style == "Heading 2" and current_website:
            current_finding_section = text
            current_website["sections"][current_finding_section] = {
                "findings": [],
                "recommendations": []
            }
        
        # Extract findings (look for status symbols)
        if any(text.startswith(sym) for sym in ["✓", "⚠", "✗", "?"]):
            if current_website and current_finding_section:
                # Determine status
                status = "pass" if text.startswith("✓") else \
                         "warning" if text.startswith("⚠") else \
                         "fail" if text.startswith("✗") else "not_checked"
                
                # Determine severity from [LEVEL] marker
                severity = "low"
                if "[CRITICAL]" in text:
                    severity = "critical"
                elif "[HIGH]" in text:
                    severity = "high"
                elif "[MEDIUM]" in text:
                    severity = "medium"
                
                finding = {
                    "status": status,
                    "severity": severity,
                    "description": text,
                    "evidence": ""
                }
                current_website["sections"][current_finding_section]["findings"].append(finding)
        
        # Extract evidence lines
        if text.startswith("Evidence:"):
            if current_website and current_finding_section:
                findings = current_website["sections"][current_finding_section]["findings"]
                if findings:
                    findings[-1]["evidence"] = text.replace("Evidence:", "").strip()
        
        # Extract recommendations (look for priority symbols)
        if any(text.startswith(sym) for sym in ["🔴", "🟡", "🟢"]):
            if current_website and current_finding_section:
                priority = "high" if text.startswith("🔴") else \
                          "medium" if text.startswith("🟡") else "low"
                
                # Extract description and effort
                desc = text
                effort = "medium"
                if "(Effort:" in text:
                    effort_start = text.find("(Effort:") + 9
                    effort_end = text.find(")", effort_start)
                    if effort_end > effort_start:
                        effort = text[effort_start:effort_end]
                        desc = text[:text.find("(Effort:")].strip()
                
                rec = {
                    "priority": priority,
                    "effort": effort,
                    "description": desc
                }
                current_website["sections"][current_finding_section]["recommendations"].append(rec)
    
    # Check for credentials usage
    for website in data["websites"]:
        for section_name, section_data in website.get("sections", {}).items():
            if "Plugin" in section_name:
                for finding in section_data.get("findings", []):
                    if "WordPress version" in finding.get("description", ""):
                        data["credentials_used"]["wordpress_admin"] = True
                    if "Total plugins" in finding.get("description", ""):
                        data["credentials_used"]["wordpress_admin"] = True
            
            if "Analytics" in section_name:
                data["credentials_used"]["google_analytics"] = True
    
    return data


def create_enhancement_prompt(assessment_data: dict[str, Any], prompt_template: str) -> str:
    """Create the full prompt for LLM enhancement."""
    
    # Convert assessment data to JSON string
    data_json = json.dumps(assessment_data, indent=2, ensure_ascii=False)
    
    # Append data to prompt template
    full_prompt = prompt_template + "\n\n---\n\n## Assessment Data\n\n```json\n" + data_json + "\n```"
    
    return full_prompt


def enhance_report(input_doc_path: Path, output_doc_path: Path, prompt_path: Path) -> Path:
    """
    Enhance a Python-generated assessment report using LLM.
    
    This function:
    1. Extracts structured data from the input document
    2. Creates a prompt for LLM enhancement
    3. Returns the prompt (to be sent to LLM API)
    4. (LLM generates enhanced document separately)
    """
    
    # Load prompt template
    with open(prompt_path, "r") as f:
        prompt_template = f.read()
    
    # Extract assessment data
    assessment_data = extract_assessment_data(input_doc_path)
    
    # Create enhancement prompt
    full_prompt = create_enhancement_prompt(assessment_data, prompt_template)
    
    # Save prompt to file (for review or API submission)
    prompt_output_path = output_doc_path.parent / "enhancement_prompt.txt"
    with open(prompt_output_path, "w") as f:
        f.write(full_prompt)
    
    print(f"✓ Extracted assessment data from: {input_doc_path}")
    print(f"✓ Enhancement prompt saved to: {prompt_output_path}")
    print(f"✓ Assessment summary:")
    print(f"  - Websites: {len(assessment_data['websites'])}")
    print(f"  - WordPress admin used: {assessment_data['credentials_used']['wordpress_admin']}")
    print(f"  - Google Analytics detected: {assessment_data['credentials_used']['google_analytics']}")
    
    return prompt_output_path


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python enhance_report.py <input_doc_path> [output_doc_path]")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else input_path.parent / "enhanced_report.docx"
    prompt_path = Path(__file__).parent.parent / "prompts" / "report_enhancement.txt"
    
    enhance_report(input_path, output_path, prompt_path)
