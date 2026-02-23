"""Query interface for document collections."""

from __future__ import annotations

import logging
from pathlib import Path

from elt_doc_rag.config import RagConfig
from elt_llm_rag.query import query_index

logger = logging.getLogger(__name__)


def query_collection(
    config: RagConfig,
    collection_name: str,
    query: str,
) -> dict:
    """Query a single document collection.

    Args:
        config: RAG configuration.
        collection_name: Name of the collection to query.
        query: Query string.

    Returns:
        Dictionary with 'response' and 'source_nodes' keys.

    Raises:
        ValueError: If collection not found.
    """
    logger.info("Querying collection '%s': %s", collection_name, query)

    collection = config.get_collection(collection_name)
    if not collection:
        raise ValueError(f"Collection not found: {collection_name}")

    query_config = config.to_query_config(collection_name)

    result = query_index(
        query=query,
        persist_dir=query_config["persist_dir"],
        collection_name=collection_name,
        embedding_model=query_config["embedding_model"],
        llm_model=query_config["llm_model"],
        base_url=query_config["base_url"],
        similarity_top_k=query_config["similarity_top_k"],
        system_prompt=query_config["system_prompt"],
    )

    logger.info("Query complete")
    return result


def main() -> None:
    """CLI entry point for querying."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Query document collections in RAG index"
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
        required=True,
        help="Collection to query",
    )
    parser.add_argument(
        "--query",
        "-q",
        type=str,
        help="Query string (if not provided, runs interactive mode)",
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

    if args.query:
        # Single query mode
        try:
            result = query_collection(config, args.collection, args.query)
            print("\n=== Response ===\n")
            print(result["response"])
            print("\n=== Sources ===\n")
            for i, source in enumerate(result["source_nodes"], 1):
                print(f"[{i}] Score: {source['score']:.4f}")
                print(f"    {source['text'][:200]}...")
        except ValueError as e:
            print(f"Error: {e}")
            raise SystemExit(1)
    else:
        # Interactive mode
        collection = config.get_collection(args.collection)
        if not collection:
            print(f"Collection not found: {args.collection}")
            raise SystemExit(1)

        print("\n=== RAG Query Interface ===")
        print(f"Collection: {collection.display_name} ({collection.name})")
        print("Type 'quit' or 'exit' to stop\n")

        while True:
            try:
                user_input = input("\n> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break

            if user_input.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break

            if not user_input:
                continue

            try:
                result = query_collection(config, args.collection, user_input)
                print("\n=== Response ===\n")
                print(result["response"])
                print(f"\n[Sources: {len(result['source_nodes'])}]")
            except ValueError as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    main()
