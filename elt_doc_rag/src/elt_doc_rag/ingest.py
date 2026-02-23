"""Ingestion pipeline for document collections."""

from __future__ import annotations

import logging
from pathlib import Path

from elt_doc_rag.config import RagConfig
from elt_llm_rag.ingest import run_ingestion_pipeline

logger = logging.getLogger(__name__)


def ingest_collection(
    config: RagConfig,
    collection_name: str,
) -> int:
    """Ingest a single document collection.

    Args:
        config: RAG configuration.
        collection_name: Name of the collection to ingest.

    Returns:
        Number of documents indexed.

    Raises:
        ValueError: If collection not found or has no files.
    """
    logger.info("Ingesting collection: %s", collection_name)

    collection = config.get_collection(collection_name)
    if not collection:
        raise ValueError(f"Collection not found: {collection_name}")

    if not collection.file_paths:
        raise ValueError(f"Collection has no file paths: {collection_name}")

    if not collection.enabled:
        logger.warning("Collection is disabled: %s", collection_name)
        return 0

    ingest_config = config.to_ingest_config(collection_name)

    index = run_ingestion_pipeline(
        file_paths=collection.file_paths,
        persist_dir=ingest_config["persist_dir"],
        collection_name=collection_name,
        chunk_size=collection.chunk_size,
        chunk_overlap=collection.chunk_overlap,
        embedding_model=config.embedding_model,
        base_url=config.base_url,
        metadata=collection.metadata,
    )

    doc_count = len(index.docstore.docs) if index.docstore else 0
    logger.info(
        "Collection '%s' ingested: %d documents, %d chunks",
        collection_name,
        len(collection.file_paths),
        doc_count,
    )

    return doc_count


def ingest_all_collections(
    config: RagConfig,
    skip_disabled: bool = True,
) -> dict[str, int]:
    """Ingest all configured document collections.

    Args:
        config: RAG configuration.
        skip_disabled: If True, skip disabled collections.

    Returns:
        Dictionary mapping collection names to document counts.
    """
    results: dict[str, int] = {}

    for collection in config.collections:
        if skip_disabled and not collection.enabled:
            logger.info("Skipping disabled collection: %s", collection.name)
            continue

        try:
            count = ingest_collection(config, collection.name)
            results[collection.name] = count
        except Exception as e:
            logger.error(
                "Failed to ingest collection '%s': %s",
                collection.name,
                e,
            )
            results[collection.name] = -1

    return results


def main() -> None:
    """CLI entry point for ingestion."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Ingest document collections into RAG index"
    )
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        required=True,
        help="Path to configuration YAML file",
    )
    parser.add_argument(
        "--collection",
        type=str,
        help="Ingest a specific collection (default: all enabled)",
    )
    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Ingest all collections including disabled ones",
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

    try:
        if args.collection:
            # Single collection mode
            count = ingest_collection(config, args.collection)
            print(f"Ingested collection '{args.collection}': {count} documents")
        else:
            # All collections mode
            results = ingest_all_collections(config, skip_disabled=not args.all)

            print("\n=== Ingestion Results ===\n")
            for name, count in results.items():
                status = "OK" if count >= 0 else "FAILED"
                print(f"  {name}: {count} documents [{status}]")

            total = sum(c for c in results.values() if c >= 0)
            failed = sum(1 for c in results.values() if c < 0)

            print(f"\nTotal: {total} documents indexed")
            if failed:
                print(f"Failed: {failed} collection(s)")

    except ValueError as e:
        print(f"Error: {e}")
        raise SystemExit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
