"""Chroma vector store integration with LlamaIndex."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import chromadb
from llama_index.core import StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore

logger = logging.getLogger(__name__)


def create_chroma_vector_store(
    persist_dir: str | Path,
    collection_name: str = "documents",
) -> StorageContext:
    """Create a Chroma vector store with LlamaIndex integration.

    Args:
        persist_dir: Directory to persist Chroma data.
        collection_name: Name of the Chroma collection.

    Returns:
        StorageContext configured with Chroma vector store.
    """
    persist_path = Path(persist_dir).expanduser()
    persist_path.mkdir(parents=True, exist_ok=True)

    logger.info(
        "Creating Chroma vector store: persist_dir=%s, collection=%s",
        persist_path,
        collection_name,
    )

    # Create Chroma client
    client = chromadb.PersistentClient(path=str(persist_path))

    # Get or create collection
    collection = client.get_or_create_collection(name=collection_name)

    # Create Chroma vector store for LlamaIndex
    vector_store = ChromaVectorStore(chroma_collection=collection)

    # Create storage context
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    logger.info("Chroma vector store created successfully")
    return storage_context


def get_collection_document_count(
    persist_dir: str | Path,
    collection_name: str,
) -> int:
    """Get the number of documents in a Chroma collection.

    Args:
        persist_dir: Directory where Chroma data is persisted.
        collection_name: Name of the collection.

    Returns:
        Number of documents in the collection.
    """
    persist_path = Path(persist_dir).expanduser()
    client = chromadb.PersistentClient(path=str(persist_path))

    try:
        collection = client.get_collection(name=collection_name)
        count = collection.count()
        logger.debug("Collection '%s' has %d documents", collection_name, count)
        return count
    except Exception:
        logger.debug("Collection '%s' does not exist", collection_name)
        return 0
