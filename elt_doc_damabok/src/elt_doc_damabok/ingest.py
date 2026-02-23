"""Ingestion pipeline for DMBOK RAG system."""

from __future__ import annotations

import logging

import chromadb
import ollama

from elt_doc_damabok.constants import DEFAULT_EMBEDDING_MODEL
from elt_doc_damabok.text_processor import _chunk_pages, _extract_pages
from elt_doc_damabok.utils import (
    expand_path,
    load_doc_config,
    load_vector_config,
)

logger = logging.getLogger(__name__)


def _embed_texts(texts: list[str], model: str) -> list[list[float]]:
    """Embed a list of texts using Ollama.
    
    Args:
        texts: List of text strings to embed.
        model: Embedding model name.
        
    Returns:
        List of embedding vectors.
        
    Raises:
        RuntimeError: If embedding fails.
    """
    logger.info("Embedding %d texts with model: %s", len(texts), model)
    
    embeddings: list[list[float]] = []
    
    for i, text in enumerate(texts, start=1):
        try:
            resp = ollama.embeddings(model=model, prompt=text)
            embeddings.append(resp.embedding)
            
            if i % 10 == 0:
                logger.debug("Embedded %d/%d texts", i, len(texts))
                
        except Exception as e:
            logger.error("Failed to embed text %d: %s", i, e)
            raise RuntimeError(f"Failed to embed text {i}: {e}")
    
    logger.info("Embedded %d texts successfully", len(embeddings))
    return embeddings


def build_index() -> None:
    """Build the Chroma index from DMBOK PDF.
    
    This function:
    1. Loads configuration
    2. Extracts text from PDF
    3. Chunks the text
    4. Embeds the chunks
    5. Stores in Chroma
    
    Raises:
        FileNotFoundError: If PDF or config not found.
        RuntimeError: If any step fails.
    """
    logger.info("Starting DMBOK index build")
    
    # Load configuration
    logger.debug("Loading configuration")
    cfg = load_doc_config()
    vcfg = load_vector_config()
    
    # Extract parameters
    pdf_path = expand_path(cfg["source_pdf"])
    chunk_size = int(cfg.get("chunk_size", DEFAULT_CHUNK_SIZE))
    chunk_overlap = int(cfg.get("chunk_overlap", DEFAULT_CHUNK_OVERLAP))
    embed_model = str(vcfg.get("embedding_model", DEFAULT_EMBEDDING_MODEL))
    
    chroma_cfg = vcfg.get("chroma", {})
    persist_dir = expand_path(chroma_cfg.get("persist_dir", "./damabok_chroma"))
    collection_name = str(chroma_cfg.get("collection_name", "damabok"))
    
    logger.info(
        "Configuration: pdf=%s, chunk_size=%d, overlap=%d, model=%s, persist_dir=%s",
        pdf_path,
        chunk_size,
        chunk_overlap,
        embed_model,
        persist_dir,
    )
    
    # Ensure persist directory exists
    persist_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract text
    pages = _extract_pages(pdf_path)
    
    # Chunk text
    chunks = _chunk_pages(pages, max_chars=chunk_size, overlap=chunk_overlap)
    
    # Initialize Chroma
    logger.info("Initializing Chroma client: %s", persist_dir)
    client = chromadb.PersistentClient(path=str(persist_dir))
    
    # Delete and recreate collection
    logger.info("Recreating collection: %s", collection_name)
    try:
        client.delete_collection(collection_name)
        logger.debug("Deleted existing collection")
    except Exception:
        logger.debug("No existing collection to delete")
    
    collection = client.get_or_create_collection(collection_name)
    
    # Embed chunks
    embeddings = _embed_texts(chunks, model=embed_model)
    
    # Store in Chroma
    logger.info("Storing %d embeddings in Chroma", len(embeddings))
    ids = [f"chunk-{i}" for i in range(len(chunks))]
    collection.add(ids=ids, embeddings=embeddings, documents=chunks)
    
    logger.info("Index build complete: %d chunks stored", len(chunks))


def main() -> None:
    """CLI entry point for ingestion."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build DMBOK RAG index")
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
    
    try:
        build_index()
        print("DMBOK index built successfully")
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        raise SystemExit(1)
    except RuntimeError as e:
        print(f"Error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
