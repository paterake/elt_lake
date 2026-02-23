"""Document chunking using LlamaIndex transformers."""

from __future__ import annotations

import logging
from typing import Any

from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter, SemanticSplitterNodeParser
from llama_index.embeddings.ollama import OllamaEmbedding

logger = logging.getLogger(__name__)


def create_sentence_splitter(
    chunk_size: int = 1024,
    chunk_overlap: int = 200,
    paragraph_separator: str = "\n\n\n",
) -> SentenceSplitter:
    """Create a sentence-aware chunk splitter.

    This splitter respects sentence and paragraph boundaries,
    avoiding mid-sentence cuts where possible.

    Args:
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Overlap between consecutive chunks.
        paragraph_separator: String used to identify paragraph breaks.

    Returns:
        Configured SentenceSplitter instance.
    """
    logger.info(
        "Creating SentenceSplitter: chunk_size=%d, overlap=%d",
        chunk_size,
        chunk_overlap,
    )

    return SentenceSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        paragraph_separator=paragraph_separator,
    )


def create_semantic_splitter(
    embedding_model: str = "nomic-embed-text",
    base_url: str = "http://localhost:11434",
    buffer_size: int = 1,
    sentence_split_threshold: float = 0.5,
) -> SemanticSplitterNodeParser:
    """Create a semantic chunk splitter.

    This splitter uses embeddings to identify semantic boundaries,
    creating chunks that are more coherent in meaning.

    Args:
        embedding_model: Ollama embedding model name.
        base_url: Ollama server base URL.
        buffer_size: Number of sentences to buffer for context.
        sentence_split_threshold: Threshold for splitting sentences.

    Returns:
        Configured SemanticSplitterNodeParser instance.
    """
    logger.info(
        "Creating SemanticSplitterNodeParser: model=%s, threshold=%f",
        embedding_model,
        sentence_split_threshold,
    )

    embed_model = OllamaEmbedding(
        model_name=embedding_model,
        base_url=base_url,
    )

    return SemanticSplitterNodeParser(
        buffer_size=buffer_size,
        sentence_split_threshold=sentence_split_threshold,
        embed_model=embed_model,
    )


def chunk_documents(
    documents: list[Document],
    chunk_size: int = 1024,
    chunk_overlap: int = 200,
    use_semantic: bool = False,
    embedding_model: str = "nomic-embed-text",
    base_url: str = "http://localhost:11434",
) -> list[Any]:
    """Chunk documents using the specified strategy.

    Args:
        documents: List of LlamaIndex Document objects.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Overlap between consecutive chunks.
        use_semantic: If True, use semantic splitting; otherwise sentence splitting.
        embedding_model: Ollama embedding model (used if use_semantic=True).
        base_url: Ollama server base URL.

    Returns:
        List of node objects (chunks with metadata).
    """
    logger.info(
        "Chunking %d documents (semantic=%s, chunk_size=%d, overlap=%d)",
        len(documents),
        use_semantic,
        chunk_size,
        chunk_overlap,
    )

    if use_semantic:
        splitter = create_semantic_splitter(
            embedding_model=embedding_model,
            base_url=base_url,
        )
    else:
        splitter = create_sentence_splitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    nodes = splitter.get_nodes_from_documents(documents)

    logger.info("Created %d chunks from %d documents", len(nodes), len(documents))
    return nodes
