"""Configuration loader for assessment."""

import os
from pathlib import Path
from typing import Any

import yaml

from .models.assessment import (
    AssessmentConfig,
    Credential,
    Requirement,
    Website,
)


def load_config(config_path: Path) -> AssessmentConfig:
    """Load assessment configuration from YAML file."""
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)

    # Parse assessment metadata
    assessment = data.get("assessment", {})
    name = assessment.get("name", "Website Assessment")
    description = assessment.get("description", "")

    # Parse URLs
    websites: list[Website] = []
    information_urls: list[Website] = []

    for url_entry in data.get("urls", []):
        website = Website(
            url=url_entry["url"],
            name=url_entry.get("name", url_entry["url"]),
            category=url_entry.get("category", "assess"),
        )
        if website.category == "assess":
            websites.append(website)
        elif website.category == "information":
            information_urls.append(website)

    # Parse requirements (sorted by sequence)
    requirements: list[Requirement] = []
    for doc in data.get("Documents", []):
        if doc.get("category") == "requirement":
            # Parse description to extract section/subsection
            description_text = doc.get("description", "")
            section, subsection = _parse_requirement_description(description_text)
            
            requirements.append(Requirement(
                section=section,
                subsection=subsection,
                description=description_text,
                sequence=int(doc.get("sequence", 99)),
                category=doc.get("category", "requirement"),
            ))
    
    # Sort by sequence
    requirements.sort(key=lambda r: r.sequence)

    # Parse credentials
    credentials: Credential | None = None
    creds_path = data.get("credentials")
    if creds_path:
        # Resolve relative to config file
        creds_file = config_path.parent / creds_path
        if creds_file.exists():
            with open(creds_file, "r") as f:
                creds_data = yaml.safe_load(f)
                if creds_data and len(creds_data) > 0:
                    cred = creds_data[0]
                    credentials = Credential(
                        username=cred.get("username", ""),
                        password=cred.get("password", ""),
                    )

    # Parse output path
    output_path_str = data.get("output", "assessment_report.docx")
    output_path = _resolve_output_path(config_path, output_path_str)

    return AssessmentConfig(
        name=name,
        description=description,
        websites=websites,
        information_urls=information_urls,
        requirements=requirements,
        credentials=credentials,
        output_path=output_path,
    )


def _parse_requirement_description(description: str) -> tuple[str, str]:
    """Parse requirement description to extract section and subsection."""
    # Default values
    section = "General"
    subsection = description
    
    # Try to extract section from common patterns
    if "part" in description.lower():
        section = description
    
    return section, subsection


def _resolve_output_path(config_path: Path, output_path: str) -> Path:
    """Resolve output path relative to config file."""
    output = Path(output_path)
    if not output.is_absolute():
        # Resolve relative to config file
        output = config_path.parent / output
    return output.expanduser().resolve()


def expand_user_path(path_str: str) -> Path:
    """Expand ~ to user home directory."""
    return Path(path_str).expanduser()
