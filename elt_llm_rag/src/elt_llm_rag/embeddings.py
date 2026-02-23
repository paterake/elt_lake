"""Embedding model utilities for LlamaIndex with Ollama."""

from __future__ import annotations

import logging

from llama_index.core import Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama

logger = logging.getLogger(__name__)


def create_embedding_model(
    model_name: str = "nomic-embed-text",
    base_url: str = "http://localhost:11434",
    embed_batch_size: int = 10,
) -> OllamaEmbedding:
    """Create an Ollama embedding model.

    Args:
        model_name: Ollama embedding model name.
        base_url: Ollama server base URL.
        embed_batch_size: Number of texts to embed in each batch.

    Returns:
        Configured OllamaEmbedding instance.
    """
    logger.info(
        "Creating Ollama embedding model: %s (batch_size=%d)",
        model_name,
        embed_batch_size,
    )

    return OllamaEmbedding(
        model_name=model_name,
        base_url=base_url,
        embed_batch_size=embed_batch_size,
    )


def create_llm_model(
    model_name: str = "llama3.2",
    base_url: str = "http://localhost:11434",
    context_window: int = 4096,
    request_timeout: float = 60.0,
) -> Ollama:
    """Create an Ollama LLM model.

    Args:
        model_name: Ollama LLM model name.
        base_url: Ollama server base URL.
        context_window: Maximum context window size.
        request_timeout: Request timeout in seconds.

    Returns:
        Configured Ollama LLM instance.
    """
    logger.info(
        "Creating Ollama LLM model: %s (context_window=%d)",
        model_name,
        context_window,
    )

    return Ollama(
        model=model_name,
        base_url=base_url,
        request_timeout=request_timeout,
        context_window=context_window,
    )


def configure_global_settings(
    embed_model: OllamaEmbedding | None = None,
    llm_model: Ollama | None = None,
    chunk_size: int = 512,
    chunk_overlap: int = 128,
) -> None:
    """Configure LlamaIndex global settings.

    Args:
        embed_model: Embedding model instance.
        llm_model: LLM model instance.
        chunk_size: Default chunk size for transformations.
        chunk_overlap: Default chunk overlap for transformations.
    """
    logger.info("Configuring LlamaIndex global settings")

    if embed_model:
        Settings.embed_model = embed_model
    if llm_model:
        Settings.llm = llm_model
    Settings.chunk_size = chunk_size
    Settings.chunk_overlap = chunk_overlap

    logger.info("LlamaIndex global settings configured")
