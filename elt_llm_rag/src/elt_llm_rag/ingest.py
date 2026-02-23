"""Ingestion pipeline using LlamaIndex for document processing."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from llama_index.core import (
    Document,
    Settings,
    VectorStoreIndex,
    StorageContext,
)
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.ollama import OllamaEmbedding

from elt_llm_rag.vector_store import create_chroma_vector_store
from elt_llm_rag.embeddings import create_embedding_model

logger = logging.getLogger(__name__)


def load_documents(
    file_paths: list[str | Path],
    metadata: dict[str, Any] | None = None,
) -> list[Document]:
    """Load documents from file paths.

    Supports multiple file formats via LlamaIndex readers:
    - PDF (.pdf)
    - Word (.docx)
    - Text (.txt)
    - HTML (.html)
    - And more...

    Args:
        file_paths: List of file paths to load.
        metadata: Optional metadata to attach to all documents.

    Returns:
        List of LlamaIndex Document objects.
    """
    from llama_index.readers.file import FlatReader

    logger.info("Loading %d documents", len(file_paths))

    documents: list[Document] = []
    reader = FlatReader()

    for file_path in file_paths:
        path = Path(file_path).expanduser()
        logger.debug("Loading document: %s", path)

        if not path.exists():
            logger.warning("File not found, skipping: %s", path)
            continue

        try:
            docs = reader.load_data(path)
            for doc in docs:
                if metadata:
                    doc.metadata.update(metadata)
                doc.metadata["source_file"] = str(path)
            documents.extend(docs)
            logger.info("Loaded document: %s (%d chars)", path, len(doc.text or ""))
        except Exception as e:
            logger.error("Failed to load %s: %s", path, e)

    logger.info("Loaded %d documents total", len(documents))
    return documents


def build_index(
    documents: list[Document],
    storage_context: StorageContext,
    chunk_size: int = 1024,
    chunk_overlap: int = 200,
    embed_model: OllamaEmbedding | None = None,
) -> VectorStoreIndex:
    """Build a vector index from documents.

    Args:
        documents: List of Document objects to index.
        storage_context: Chroma storage context.
        chunk_size: Chunk size for splitting.
        chunk_overlap: Overlap between chunks.
        embed_model: Optional embedding model (uses Settings if not provided).

    Returns:
        VectorStoreIndex containing the embedded documents.
    """
    logger.info(
        "Building index from %d documents (chunk_size=%d, overlap=%d)",
        len(documents),
        chunk_size,
        chunk_overlap,
    )

    # Set embedding model if provided
    if embed_model:
        Settings.embed_model = embed_model

    # Create index with storage context
    index = VectorStoreIndex.from_documents(
        documents=documents,
        storage_context=storage_context,
        transformations=[
            SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap),
        ],
        show_progress=True,
    )

    logger.info("Index built successfully with %d documents", len(documents))
    return index


def run_ingestion_pipeline(
    file_paths: list[str | Path],
    persist_dir: str | Path,
    collection_name: str,
    chunk_size: int = 1024,
    chunk_overlap: int = 200,
    embedding_model: str = "nomic-embed-text",
    base_url: str = "http://localhost:11434",
    metadata: dict[str, Any] | None = None,
) -> VectorStoreIndex:
    """Run the complete ingestion pipeline.

    Args:
        file_paths: List of file paths to ingest.
        persist_dir: Directory to persist Chroma data.
        collection_name: Name of the Chroma collection.
        chunk_size: Chunk size for splitting.
        chunk_overlap: Overlap between chunks.
        embedding_model: Ollama embedding model name.
        base_url: Ollama server base URL.
        metadata: Optional metadata to attach to documents.

    Returns:
        VectorStoreIndex containing the ingested documents.
    """
    logger.info("Starting ingestion pipeline")

    # Create embedding model
    embed_model = create_embedding_model(
        model_name=embedding_model,
        base_url=base_url,
    )

    # Create storage context
    storage_context = create_chroma_vector_store(
        persist_dir=persist_dir,
        collection_name=collection_name,
    )

    # Load documents
    documents = load_documents(file_paths, metadata)

    if not documents:
        raise ValueError("No documents were loaded. Check file paths.")

    # Build index
    index = build_index(
        documents=documents,
        storage_context=storage_context,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        embed_model=embed_model,
    )

    logger.info("Ingestion pipeline complete")
    return index


def main() -> None:
    """CLI entry point for ingestion."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Build RAG index using LlamaIndex")
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        required=True,
        help="Path to configuration JSON file",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Load configuration
    config_path = Path(args.config).expanduser()
    with open(config_path) as f:
        config = json.load(f)

    try:
        index = run_ingestion_pipeline(
            file_paths=config.get("file_paths", []),
            persist_dir=config.get("persist_dir", "./chroma_db"),
            collection_name=config.get("collection_name", "documents"),
            chunk_size=config.get("chunk_size", 1024),
            chunk_overlap=config.get("chunk_overlap", 200),
            embedding_model=config.get("embedding_model", "nomic-embed-text"),
            base_url=config.get("base_url", "http://localhost:11434"),
            metadata=config.get("metadata"),
        )
        print(f"Ingestion complete: {len(index.docstore.docs)} documents indexed")
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        raise SystemExit(1)
    except ValueError as e:
        print(f"Error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
