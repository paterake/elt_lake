from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import ollama


def expand_path(path_str: str) -> Path:
    return Path(os.path.expanduser(path_str)).resolve()


def _load_json_config(filename: str) -> dict[str, Any]:
    here = Path(__file__).resolve().parent.parent.parent
    cfg_path = here / "config" / filename
    try:
        with cfg_path.open() as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {cfg_path}")
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse JSON config {cfg_path}: {exc}") from exc


def load_doc_config() -> dict[str, Any]:
    return _load_json_config("doc_damabok.json")


def load_vector_config() -> dict[str, Any]:
    return _load_json_config("vector_db.json")


def load_ollama_config() -> dict[str, Any]:
    return _load_json_config("ollama.json")


def embed_query(query: str, model: str) -> list[float]:
    resp = ollama.embeddings(model=model, prompt=query)
    return resp.embedding


def build_prompt(
    question: str,
    contexts: list[str],
    system_prompt: str,
    max_prompt_chars: int,
) -> str:
    parts: list[str] = [system_prompt, ""]
    char_count = sum(len(p) for p in parts) + len(parts) - 1
    for i, c in enumerate(contexts, start=1):
        header = f"Excerpt {i}:"
        block = [header, c, ""]
        block_text = "\n".join(block)
        if char_count + len(block_text) + 1 > max_prompt_chars:
            break
        parts.extend(block)
        char_count += len(block_text) + 1
    parts.append(f"Question: {question}")
    parts.append("Answer:")
    return "\n".join(parts)

