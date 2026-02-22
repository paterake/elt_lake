"""Configuration loader for SAD template."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _get_config_dir() -> Path:
    """Get the config directory path."""
    return Path(__file__).resolve().parent.parent.parent / "config"


def load_sad_template() -> dict[str, Any]:
    """Load the SAD template structure.
    
    Returns:
        Dictionary containing the SAD template structure with sections and subsections.
    """
    config_path = _get_config_dir() / "sad_template.json"
    with config_path.open() as f:
        return json.load(f)


def load_section_guidance() -> dict[str, Any]:
    """Load the section guidance content.
    
    Returns:
        Dictionary containing guidance for each SAD section.
    """
    config_path = _get_config_dir() / "section_guidance.json"
    with config_path.open() as f:
        return json.load(f)


def load_integration_patterns() -> dict[str, Any]:
    """Load the integration patterns.
    
    Returns:
        Dictionary containing integration pattern definitions.
    """
    config_path = _get_config_dir() / "integration_patterns.json"
    with config_path.open() as f:
        return json.load(f)


def get_section_guidance(section_id: str) -> dict[str, Any] | None:
    """Get guidance for a specific section.
    
    Args:
        section_id: Section identifier (e.g., "1.1", "2.3", "3.1").
        
    Returns:
        Guidance dictionary for the section, or None if not found.
    """
    guidance = load_section_guidance()
    # Map section IDs to guidance keys
    section_names = {
        "1.1": "1.1 Objectives",
        "1.2": "1.2 Functionality",
        "1.3": "1.3 Constraints",
        "1.4": "1.4 Dependencies",
        "1.5": "1.5 Legacy",
        "2.1": "2.1 GDPR",
        "2.2": "2.2 Sources",
        "2.3": "2.3 Integration",
        "2.4": "2.4 Migration",
        "2.5": "2.5 Audit",
        "2.6": "2.6 Backups",
        "2.7": "2.7 Reporting",
        "3.1": "3.1 Security",
        "3.2": "3.2 Capacity",
        "3.3": "3.3 Performance",
        "3.4": "3.4 Scalability",
        "3.5": "3.5 Availability",
        "3.6": "3.6 Disaster Recovery",
        "3.7": "3.7 Monitoring",
        "4.1": "4.1 Application Architecture",
        "4.2": "4.2 Infrastructure Architecture",
        "4.3": "4.3 Environments",
        "4.4": "4.4 DevOps",
        "5.1": "5.1 Infrastructure",
        "5.2": "5.2 Data",
        "5.3": "5.3 Development",
        "6.1": "6.1 Infrastructure",
        "6.2": "6.2 Application",
        "6.3": "6.3 Software",
        "7.1": "7.1 Support",
        "7.2": "7.2 Roadmap",
        "7.3": "7.3 Life Expectancy",
        "8.1": "8.1 Test Scenarios",
        "8.2": "8.2 Data Mappings",
        "8.3": "8.3 Security Configuration Details",
    }
    key = section_names.get(section_id)
    if key:
        return guidance.get(key)
    return None


def get_pattern_by_id(pattern_id: str) -> dict[str, Any] | None:
    """Get an integration pattern by ID.
    
    Args:
        pattern_id: Pattern identifier (e.g., "outbound_eib_sftp").
        
    Returns:
        Pattern dictionary, or None if not found.
    """
    patterns = load_integration_patterns()
    return patterns.get("patterns", {}).get(pattern_id)
