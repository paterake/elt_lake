# elt-llm-rag

LlamaIndex-based RAG core for document chunking, embedding, and retrieval with Chroma and Ollama.

## Overview

This package provides the core RAG (Retrieval-Augmented Generation) infrastructure using:

- **LlamaIndex** - Document loading, chunking, and index management
- **Chroma** - Vector database for embeddings
- **Ollama** - Local embedding and LLM models

## Features

- **Multi-format document loading** - PDF, DOCX, TXT, HTML, and more
- **Sentence-aware chunking** - Respects sentence/paragraph boundaries
- **Semantic chunking** - Optional embedding-based chunk boundaries
- **Persistent vector storage** - ChromaDB with named collections
- **Local inference** - Ollama-based embeddings and LLM

## Installation

From the workspace root:

```bash
cd elt_llm_rag
uv sync
```

## Configuration

Create a JSON configuration file:

```json
{
  "file_paths": ["/path/to/document.pdf"],
  "persist_dir": "./chroma_db",
  "collection_name": "my_documents",
  "chunk_size": 1024,
  "chunk_overlap": 200,
  "embedding_model": "nomic-embed-text",
  "llm_model": "llama3.2",
  "base_url": "http://localhost:11434",
  "metadata": {
    "domain": "example"
  }
}
```

## Usage

### Ingestion (Build Index)

```bash
uv run python -m elt_llm_rag.ingest --config config.json
```

Or programmatically:

```python
from elt_llm_rag.ingest import run_ingestion_pipeline

index = run_ingestion_pipeline(
    file_paths=["/path/to/document.pdf"],
    persist_dir="./chroma_db",
    collection_name="my_documents",
    chunk_size=1024,
    chunk_overlap=200,
    embedding_model="nomic-embed-text",
)
```

### Querying

```bash
# Single query
uv run python -m elt_llm_rag.query --config config.json --query "What is data governance?"

# Interactive mode
uv run python -m elt_llm_rag.query --config config.json
```

Or programmatically:

```python
from elt_llm_rag.query import query_index

result = query_index(
    query="What is data governance?",
    persist_dir="./chroma_db",
    collection_name="my_documents",
    embedding_model="nomic-embed-text",
    llm_model="llama3.2",
)

print(result["response"])
print(result["source_nodes"])  # Retrieved chunks with scores
```

## Module Structure

```
elt_llm_rag/
├── __init__.py          # Package initialization
├── ingest.py            # Document ingestion pipeline
├── query.py             # Query interface
├── vector_store.py      # Chroma integration
├── chunker.py           # Chunking strategies
└── embeddings.py        # Ollama embedding/LLM setup
```

## Chunking Strategies

### Sentence Splitting (Default)

Respects sentence and paragraph boundaries:

```python
from elt_llm_rag.chunker import create_sentence_splitter

splitter = create_sentence_splitter(
    chunk_size=1024,
    chunk_overlap=200,
)
```

### Semantic Splitting

Uses embeddings to identify semantic boundaries:

```python
from elt_llm_rag.chunker import create_semantic_splitter

splitter = create_semantic_splitter(
    embedding_model="nomic-embed-text",
    sentence_split_threshold=0.5,
)
```

## Prerequisites

- Python 3.11, 3.12, or 3.13 (ChromaDB is not yet compatible with Python 3.14)
- Ollama running locally (`ollama serve`)
- Required models pulled:
  ```bash
  ollama pull nomic-embed-text
  ollama pull llama3.2
  ```

**Note:** If you're using Python 3.14+, you'll need to downgrade to Python 3.11-3.13 due to ChromaDB's pydantic v1 compatibility issues.
