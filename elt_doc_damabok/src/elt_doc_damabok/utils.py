"""Configuration loader for elt_doc_damabok module."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Module-level cache for config files
_config_cache: dict[str, dict[str, Any]] = {}


def _get_config_dir() -> Path:
    """Get the config directory path.
    
    Returns:
        Path to the config directory.
    """
    return Path(__file__).resolve().parent.parent.parent / "config"


def _load_json_config(filename: str, use_cache: bool = True) -> dict[str, Any]:
    """Load a JSON config file with error handling and caching.
    
    Args:
        filename: Name of the config file (e.g., "doc_damabok.json").
        use_cache: Whether to use cached config (default True).
        
    Returns:
        Parsed JSON content as dictionary.
        
    Raises:
        FileNotFoundError: If config file does not exist.
        RuntimeError: If config file contains invalid JSON.
        PermissionError: If config file cannot be read.
    """
    cache_key = f"config_{filename}"
    
    if use_cache and cache_key in _config_cache:
        logger.debug("Using cached config: %s", filename)
        return _config_cache[cache_key]
    
    config_dir = _get_config_dir()
    cfg_path = config_dir / filename
    
    try:
        logger.debug("Loading config from: %s", cfg_path)
        with cfg_path.open(encoding="utf-8") as f:
            config = json.load(f)
        
        if use_cache:
            _config_cache[cache_key] = config
            logger.debug("Cached config: %s", filename)
        
        return config
        
    except FileNotFoundError:
        logger.error("Config file not found: %s", cfg_path)
        raise FileNotFoundError(f"Config file not found: {cfg_path}")
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in config file %s: %s", cfg_path, e)
        raise RuntimeError(f"Failed to parse JSON config {cfg_path}: {e}")
    except PermissionError:
        logger.error("Permission denied reading config file: %s", cfg_path)
        raise PermissionError(f"Permission denied reading config file: {cfg_path}")


def expand_path(path_str: str) -> Path:
    """Expand user path and resolve to absolute path.
    
    Args:
        path_str: Path string that may contain ~ for home directory.
        
    Returns:
        Resolved absolute Path.
    """
    import os
    return Path(os.path.expanduser(path_str)).resolve()


def load_doc_config(use_cache: bool = True) -> dict[str, Any]:
    """Load the document configuration.
    
    Args:
        use_cache: Whether to use cached config (default True).
        
    Returns:
        Dictionary containing document configuration.
        
    Raises:
        FileNotFoundError: If config file does not exist.
        RuntimeError: If config file contains invalid JSON.
    """
    return _load_json_config("doc_damabok.json", use_cache)


def load_vector_config(use_cache: bool = True) -> dict[str, Any]:
    """Load the vector database configuration.
    
    Args:
        use_cache: Whether to use cached config (default True).
        
    Returns:
        Dictionary containing vector database configuration.
        
    Raises:
        FileNotFoundError: If config file does not exist.
        RuntimeError: If config file contains invalid JSON.
    """
    return _load_json_config("vector_db.json", use_cache)


def load_ollama_config(use_cache: bool = True) -> dict[str, Any]:
    """Load the Ollama configuration.
    
    Args:
        use_cache: Whether to use cached config (default True).
        
    Returns:
        Dictionary containing Ollama configuration.
        
    Raises:
        FileNotFoundError: If config file does not exist.
        RuntimeError: If config file contains invalid JSON.
    """
    return _load_json_config("ollama.json", use_cache)


def clear_config_cache() -> None:
    """Clear the configuration cache.
    
    Useful for testing or when config files have been updated.
    """
    global _config_cache
    _config_cache = {}
    logger.debug("Config cache cleared")


def embed_query(query: str, model: str) -> list[float]:
    """Embed a query using Ollama.
    
    Args:
        query: Text to embed.
        model: Embedding model name.
        
    Returns:
        List of embedding floats.
        
    Raises:
        RuntimeError: If Ollama embedding fails.
    """
    import ollama
    
    logger.debug("Embedding query with model: %s", model)
    try:
        resp = ollama.embeddings(model=model, prompt=query)
        return resp.embedding
    except Exception as e:
        logger.error("Failed to embed query: %s", e)
        raise RuntimeError(f"Failed to embed query: {e}")


def build_prompt(
    question: str,
    contexts: list[str],
    system_prompt: str,
    max_prompt_chars: int,
) -> str:
    """Build a RAG prompt with retrieved contexts.
    
    Args:
        question: User question.
        contexts: List of retrieved context strings.
        system_prompt: System prompt to prepend.
        max_prompt_chars: Maximum prompt length in characters.
        
    Returns:
        Formatted prompt string.
    """
    parts: list[str] = [system_prompt, ""]
    char_count = sum(len(p) for p in parts) + len(parts) - 1
    
    for i, c in enumerate(contexts, start=1):
        header = f"Excerpt {i}:"
        block = [header, c, ""]
        block_text = "\n".join(block)
        if char_count + len(block_text) + 1 > max_prompt_chars:
            logger.debug(
                "Reached max_prompt_chars (%d) at context %d",
                max_prompt_chars,
                i,
            )
            break
        parts.extend(block)
        char_count += len(block_text) + 1
    
    parts.append(f"Question: {question}")
    parts.append("Answer:")
    
    logger.debug(
        "Built prompt with %d contexts, total length: %d chars",
        len(contexts),
        char_count,
    )
    
    return "\n".join(parts)
