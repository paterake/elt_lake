"""Configuration loader for SAD template."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Module-level cache for config files
_config_cache: dict[str, Any] = {}


def _get_package_root() -> Path:
    """Get the package root directory path.
    
    Returns:
        Path to the elt_doc_sad package root.
    """
    return Path(__file__).resolve().parent


def _get_config_dir() -> Path:
    """Get the config directory path.
    
    Returns:
        Path to the config directory.
    """
    return _get_package_root().parent.parent / "config"


def _get_resources_dir() -> Path:
    """Get the resources directory path.
    
    Returns:
        Path to the resources directory.
    """
    return _get_package_root().parent.parent / "resources"


def _load_json_config(config_name: str, use_cache: bool = True) -> dict[str, Any]:
    """Load a JSON config file with error handling.
    
    Args:
        config_name: Name of the config file (without .json extension).
        use_cache: Whether to use cached config (default True).
        
    Returns:
        Parsed JSON content as dictionary.
        
    Raises:
        FileNotFoundError: If config file does not exist.
        ValueError: If config file contains invalid JSON.
        PermissionError: If config file cannot be read.
    """
    cache_key = f"config_{config_name}"
    
    if use_cache and cache_key in _config_cache:
        logger.debug("Using cached config: %s", config_name)
        return _config_cache[cache_key]
    
    config_path = _get_config_dir() / f"{config_name}.json"
    
    try:
        logger.debug("Loading config from: %s", config_path)
        with config_path.open(encoding="utf-8") as f:
            config = json.load(f)
        
        if use_cache:
            _config_cache[cache_key] = config
            logger.debug("Cached config: %s", config_name)
        
        return config
        
    except FileNotFoundError:
        logger.error("Config file not found: %s", config_path)
        raise FileNotFoundError(f"Config file not found: {config_path}")
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in config file %s: %s", config_path, e)
        raise ValueError(f"Invalid JSON in {config_path}: {e}")
    except PermissionError:
        logger.error("Permission denied reading config file: %s", config_path)
        raise PermissionError(f"Permission denied reading config file: {config_path}")


def load_sad_template(use_cache: bool = True) -> dict[str, Any]:
    """Load the SAD template structure.
    
    Args:
        use_cache: Whether to use cached config (default True).
        
    Returns:
        Dictionary containing the SAD template structure with sections and subsections.
        
    Raises:
        FileNotFoundError: If config file does not exist.
        ValueError: If config file contains invalid JSON.
    """
    return _load_json_config("sad_template", use_cache)


def load_section_guidance(use_cache: bool = True) -> dict[str, Any]:
    """Load the section guidance content.
    
    Args:
        use_cache: Whether to use cached config (default True).
        
    Returns:
        Dictionary containing guidance for each SAD section.
        
    Raises:
        FileNotFoundError: If config file does not exist.
        ValueError: If config file contains invalid JSON.
    """
    return _load_json_config("section_guidance", use_cache)


def load_integration_patterns(use_cache: bool = True) -> dict[str, Any]:
    """Load the integration patterns.
    
    Args:
        use_cache: Whether to use cached config (default True).
        
    Returns:
        Dictionary containing integration pattern definitions.
        
    Raises:
        FileNotFoundError: If config file does not exist.
        ValueError: If config file contains invalid JSON.
    """
    return _load_json_config("integration_patterns", use_cache)


def get_section_guidance(section_id: str) -> dict[str, Any] | None:
    """Get guidance for a specific section.
    
    Args:
        section_id: Section identifier (e.g., "1.1", "2.3", "3.1").
        
    Returns:
        Guidance dictionary for the section, or None if not found.
        
    Raises:
        FileNotFoundError: If config file does not exist.
        ValueError: If config file contains invalid JSON.
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
        result = guidance.get(key)
        if result:
            logger.debug("Found guidance for section %s", section_id)
        else:
            logger.warning("No guidance found for section %s", section_id)
        return result
    
    logger.warning("Unknown section ID: %s", section_id)
    return None


def get_pattern_by_id(pattern_id: str) -> dict[str, Any] | None:
    """Get an integration pattern by ID.
    
    Args:
        pattern_id: Pattern identifier (e.g., "outbound_eib_sftp").
        
    Returns:
        Pattern dictionary, or None if not found.
        
    Raises:
        FileNotFoundError: If config file does not exist.
        ValueError: If config file contains invalid JSON.
    """
    patterns = load_integration_patterns()
    result = patterns.get("patterns", {}).get(pattern_id)
    
    if result:
        logger.debug("Found pattern: %s", pattern_id)
    else:
        logger.warning("Pattern not found: %s", pattern_id)
    
    return result


def get_cover_image_path() -> Path:
    """Get the path to the cover image.
    
    Returns:
        Path to the cover image file.
    """
    return _get_resources_dir() / "cover_image.jpeg"


def clear_config_cache() -> None:
    """Clear the configuration cache.
    
    Useful for testing or when config files have been updated.
    """
    global _config_cache
    _config_cache = {}
    logger.debug("Config cache cleared")
