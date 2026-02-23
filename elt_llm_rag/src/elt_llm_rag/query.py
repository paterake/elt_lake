"""Query interface using LlamaIndex for RAG retrieval."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama

from elt_llm_rag.vector_store import create_chroma_vector_store
from elt_llm_rag.embeddings import create_embedding_model, create_llm_model

logger = logging.getLogger(__name__)


def load_index(
    persist_dir: str | Path,
    collection_name: str,
    embedding_model: str = "nomic-embed-text",
    base_url: str = "http://localhost:11434",
) -> VectorStoreIndex:
    """Load an existing vector index from Chroma.

    Args:
        persist_dir: Directory where Chroma data is persisted.
        collection_name: Name of the Chroma collection.
        embedding_model: Ollama embedding model name.
        base_url: Ollama server base URL.

    Returns:
        VectorStoreIndex loaded from storage.
    """
    logger.info("Loading index from Chroma: %s / %s", persist_dir, collection_name)

    # Create embedding model
    embed_model = create_embedding_model(
        model_name=embedding_model,
        base_url=base_url,
    )
    Settings.embed_model = embed_model

    # Create storage context
    storage_context = create_chroma_vector_store(
        persist_dir=persist_dir,
        collection_name=collection_name,
    )

    # Load index from storage
    index = VectorStoreIndex.from_vector_store(
        storage_context.vector_store,
        storage_context=storage_context,
    )

    logger.info("Index loaded successfully")
    return index


def create_query_engine(
    index: VectorStoreIndex,
    llm_model: str = "llama3.2",
    base_url: str = "http://localhost:11434",
    similarity_top_k: int = 5,
    system_prompt: str | None = None,
) -> RetrieverQueryEngine:
    """Create a query engine from an index.

    Args:
        index: VectorStoreIndex to query.
        llm_model: Ollama LLM model name.
        base_url: Ollama server base URL.
        similarity_top_k: Number of similar chunks to retrieve.
        system_prompt: Optional system prompt for the LLM.

    Returns:
        RetrieverQueryEngine for querying.
    """
    logger.info("Creating query engine (similarity_top_k=%d)", similarity_top_k)

    # Create LLM
    llm = create_llm_model(
        model_name=llm_model,
        base_url=base_url,
    )
    Settings.llm = llm

    # Create retriever
    retriever = index.as_retriever(similarity_top_k=similarity_top_k)

    # Create query engine
    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        llm=llm,
    )

    logger.info("Query engine created")
    return query_engine


def query_index(
    query: str,
    persist_dir: str | Path,
    collection_name: str,
    embedding_model: str = "nomic-embed-text",
    llm_model: str = "llama3.2",
    base_url: str = "http://localhost:11434",
    similarity_top_k: int = 5,
    system_prompt: str | None = None,
) -> dict[str, Any]:
    """Query a vector index.

    Args:
        query: Query string.
        persist_dir: Directory where Chroma data is persisted.
        collection_name: Name of the Chroma collection.
        embedding_model: Ollama embedding model name.
        llm_model: Ollama LLM model name.
        base_url: Ollama server base URL.
        similarity_top_k: Number of similar chunks to retrieve.
        system_prompt: Optional system prompt for the LLM.

    Returns:
        Dictionary with 'response' and 'source_nodes' keys.
    """
    logger.info("Querying index: %s", query)

    # Load index
    index = load_index(
        persist_dir=persist_dir,
        collection_name=collection_name,
        embedding_model=embedding_model,
        base_url=base_url,
    )

    # Create query engine
    query_engine = create_query_engine(
        index=index,
        llm_model=llm_model,
        base_url=base_url,
        similarity_top_k=similarity_top_k,
        system_prompt=system_prompt,
    )

    # Execute query
    response = query_engine.query(query)

    # Format source nodes
    source_nodes = []
    for node in response.source_nodes:
        source_nodes.append(
            {
                "text": node.node.text,
                "metadata": node.node.metadata,
                "score": node.score,
            }
        )

    result = {
        "response": str(response),
        "source_nodes": source_nodes,
    }

    logger.info("Query complete")
    return result


def main() -> None:
    """CLI entry point for querying."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Query RAG index using LlamaIndex")
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        required=True,
        help="Path to configuration JSON file",
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
    config_path = Path(args.config).expanduser()
    with open(config_path) as f:
        config = json.load(f)

    if args.query:
        # Single query mode
        result = query_index(
            query=args.query,
            persist_dir=config.get("persist_dir", "./chroma_db"),
            collection_name=config.get("collection_name", "documents"),
            embedding_model=config.get("embedding_model", "nomic-embed-text"),
            llm_model=config.get("llm_model", "llama3.2"),
            base_url=config.get("base_url", "http://localhost:11434"),
            similarity_top_k=config.get("similarity_top_k", 5),
            system_prompt=config.get("system_prompt"),
        )
        print("\n=== Response ===\n")
        print(result["response"])
        print("\n=== Sources ===\n")
        for i, source in enumerate(result["source_nodes"], 1):
            print(f"[{i}] Score: {source['score']:.4f}")
            print(f"    {source['text'][:200]}...")
    else:
        # Interactive mode
        print("\n=== RAG Query Interface ===")
        print(f"Collection: {config.get('collection_name', 'documents')}")
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

            result = query_index(
                query=user_input,
                persist_dir=config.get("persist_dir", "./chroma_db"),
                collection_name=config.get("collection_name", "documents"),
                embedding_model=config.get("embedding_model", "nomic-embed-text"),
                llm_model=config.get("llm_model", "llama3.2"),
                base_url=config.get("base_url", "http://localhost:11434"),
                similarity_top_k=config.get("similarity_top_k", 5),
                system_prompt=config.get("system_prompt"),
            )

            print("\n=== Response ===\n")
            print(result["response"])
            print(f"\n[Sources: {len(result['source_nodes'])}]")


if __name__ == "__main__":
    main()
