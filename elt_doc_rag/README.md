# elt-doc-rag

Configuration-driven document collection management for RAG systems.

## Overview

This package provides a **multi-document, multi-collection** management layer on top of `elt_llm_rag`. It allows you to:

- Define multiple document collections in a single YAML config
- Ingest/query each collection independently
- Track collection status and metadata
- Scale to many documents/books with organized separation

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    documents.yaml                           │
│  - dama_dmbok collection                                    │
│  - fa_handbook collection                                   │
│  - ... more collections                                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      elt_doc_rag                            │
│  - config.py   (YAML parsing, validation)                   │
│  - ingest.py   (multi-collection ingestion)                 │
│  - query.py    (collection-scoped queries)                  │
│  - status.py   (collection diagnostics)                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     elt_llm_rag                             │
│  (LlamaIndex + Chroma + Ollama core)                        │
└─────────────────────────────────────────────────────────────┘
```

## Installation

From the workspace root:

```bash
cd elt_doc_rag
uv sync
```

This will also install `elt_llm_rag` as a dependency.

## Configuration

Create a YAML configuration file:

```yaml
# config/documents.yaml

collections:
  # DAMA-DMBOK2 Data Management Body of Knowledge
  - name: dama_dmbok
    display_name: "DAMA-DMBOK2 Data Management"
    enabled: true
    file_paths:
      - "~/Documents/__data/books/DAMA-DMBOK2R_unlocked.pdf"
    chunk_size: 1024
    chunk_overlap: 200
    use_semantic_chunking: false
    metadata:
      domain: data_management
      type: body_of_knowledge

  # FA Handbook (Financial Accounting)
  - name: fa_handbook
    display_name: "Financial Accounting Handbook"
    enabled: true
    file_paths:
      - "~/Documents/__data/books/FA_Handbook.pdf"
    chunk_size: 1024
    chunk_overlap: 200
    use_semantic_chunking: false
    metadata:
      domain: finance
      type: handbook

# Global RAG settings
persist_dir: "./chroma_db"
embedding_model: "nomic-embed-text"
llm_model: "llama3.2"
base_url: "http://localhost:11434"
similarity_top_k: 5

system_prompt: |
  You are a helpful assistant that answers questions based on the provided documents.
  Always ground your answers in the retrieved content.
```

### Configuration Options

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | required | Unique collection identifier |
| `display_name` | string | same as name | Human-readable name |
| `enabled` | bool | true | Whether to include in bulk operations |
| `file_paths` | list[string] | [] | Paths to documents |
| `chunk_size` | int | 1024 | Max characters per chunk |
| `chunk_overlap` | int | 200 | Overlap between chunks |
| `use_semantic_chunking` | bool | false | Use semantic vs sentence splitting |
| `metadata` | dict | {} | Custom metadata for all documents |

## Usage

### Check Status

```bash
uv run python -m elt_doc_rag.status --config config/documents.yaml
```

Output:
```
=== Document Collections Status ===

Persist Directory: ./chroma_db
Embedding Model: nomic-embed-text
LLM Model: llama3.2

[✓] DAMA-DMBOK2 Data Management (dama_dmbok)
    Files: 1
    Chunk Size: 1024 (overlap: 200)
    Semantic Chunking: False
    Index Status: 2847 documents indexed

[✓] Financial Accounting Handbook (fa_handbook)
    Files: 1
    Chunk Size: 1024 (overlap: 200)
    Semantic Chunking: False
    Index Status: Not indexed yet
```

### Ingest Collections

```bash
# Ingest all enabled collections
uv run python -m elt_doc_rag.ingest --config config/documents.yaml

# Ingest a specific collection
uv run python -m elt_doc_rag.ingest --config config/documents.yaml --collection dama_dmbok

# Ingest all collections (including disabled)
uv run python -m elt_doc_rag.ingest --config config/documents.yaml --all
```

### Query Collections

```bash
# Single query
uv run python -m elt_doc_rag.query \
  --config config/documents.yaml \
  --collection dama_dmbok \
  --query "What is data governance?"

# Interactive mode
uv run python -m elt_doc_rag.query \
  --config config/documents.yaml \
  --collection dama_dmbok
```

## Programmatic Usage

```python
from elt_doc_rag.config import RagConfig
from elt_doc_rag.ingest import ingest_collection
from elt_doc_rag.query import query_collection

# Load configuration
config = RagConfig.from_yaml("config/documents.yaml")

# Ingest a collection
count = ingest_collection(config, "dama_dmbok")
print(f"Ingested {count} documents")

# Query a collection
result = query_collection(
    config,
    "dama_dmbok",
    "What is data stewardship?",
)
print(result["response"])
```

## Adding New Collections

To add a new document collection:

1. Add the collection to your YAML config:
   ```yaml
   collections:
     - name: my_new_book
       display_name: "My New Book"
       file_paths:
         - "~/Documents/__data/books/my_book.pdf"
       chunk_size: 1024
       chunk_overlap: 200
   ```

2. Ingest it:
   ```bash
   uv run python -m elt_doc_rag.ingest \
     --config config/documents.yaml \
     --collection my_new_book
   ```

3. Query it:
   ```bash
   uv run python -m elt_doc_rag.query \
     --config config/documents.yaml \
     --collection my_new_book
   ```

## Module Structure

```
elt_doc_rag/
├── __init__.py          # Package initialization
├── config.py            # YAML configuration management
├── ingest.py            # Multi-collection ingestion
├── query.py             # Collection-scoped queries
└── status.py            # Collection diagnostics
```

## Prerequisites

- Python 3.11, 3.12, or 3.13 (ChromaDB is not yet compatible with Python 3.14)
- `elt_llm_rag` package installed (workspace dependency)
- Ollama running locally (`ollama serve`)
- Required models pulled:
  ```bash
  ollama pull nomic-embed-text
  ollama pull llama3.2
  ```

**Note:** If you're using Python 3.14+, you'll need to downgrade to Python 3.11-3.13 due to ChromaDB's pydantic v1 compatibility issues.

## Migration from elt_doc_damabok

If you're migrating from the original `elt_doc_damabok` module:

1. Your existing Chroma collections will continue to work
2. Create a new `documents.yaml` config pointing to your PDF
3. Use the collection name that matches your existing Chroma collection
4. Re-run ingestion to rebuild with LlamaIndex chunking
