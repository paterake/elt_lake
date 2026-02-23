"""Status and diagnostics for document collections."""

from __future__ import annotations

import logging
from pathlib import Path

import chromadb

from elt_doc_rag.config import RagConfig

logger = logging.getLogger(__name__)


def get_collection_status(
    persist_dir: str | Path,
    collection_name: str,
) -> dict:
    """Get status information for a collection.

    Args:
        persist_dir: Directory where Chroma data is persisted.
        collection_name: Name of the collection.

    Returns:
        Dictionary with collection status information.
    """
    persist_path = Path(persist_dir).expanduser()
    client = chromadb.PersistentClient(path=str(persist_path))

    try:
        collection = client.get_collection(name=collection_name)
        count = collection.count()
        return {
            "exists": True,
            "document_count": count,
            "name": collection_name,
        }
    except Exception:
        return {
            "exists": False,
            "document_count": 0,
            "name": collection_name,
        }


def show_status(config: RagConfig) -> None:
    """Show status of all configured collections.

    Args:
        config: RAG configuration.
    """
    print("\n=== Document Collections Status ===\n")
    print(f"Persist Directory: {config.persist_dir}")
    print(f"Embedding Model: {config.embedding_model}")
    print(f"LLM Model: {config.llm_model}")
    print()

    for collection in config.collections:
        status = get_collection_status(config.persist_dir, collection.name)
        enabled_str = "✓" if collection.enabled else "✗"

        print(f"[{enabled_str}] {collection.display_name} ({collection.name})")
        print(f"    Files: {len(collection.file_paths)}")
        print(f"    Chunk Size: {collection.chunk_size} (overlap: {collection.chunk_overlap})")
        print(f"    Semantic Chunking: {collection.use_semantic_chunking}")

        if status["exists"]:
            print(f"    Index Status: {status['document_count']} documents indexed")
        else:
            print(f"    Index Status: Not indexed yet")

        if collection.metadata:
            print(f"    Metadata: {collection.metadata}")
        print()


def main() -> None:
    """CLI entry point for status."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Show status of document collections"
    )
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        required=True,
        help="Path to configuration YAML file",
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
    try:
        config = RagConfig.from_yaml(args.config)
    except (FileNotFoundError, ValueError) as e:
        print(f"Configuration error: {e}")
        raise SystemExit(1)

    show_status(config)


if __name__ == "__main__":
    main()
