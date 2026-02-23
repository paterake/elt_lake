# LLM RAG Packages Setup

## Overview

This document describes the LLM RAG package structure for document ingestion and querying using LlamaIndex, ChromaDB, and Ollama.

## Package Structure

```
elt_lake/
├── elt_llm_core/           # Core RAG infrastructure
│   ├── vector_store.py     # ChromaDB tenant/database/collection setup
│   ├── models.py           # Ollama embedding and LLM models
│   ├── query_engine.py     # Query interface
│   └── config.py           # Configuration management
│
├── elt_llm_ingest/         # Generic document ingestion
│   ├── ingest.py           # Ingestion pipeline
│   └── cli.py              # CLI entry point
│
├── elt_llm_query/          # Query interface
│   ├── query.py            # Query functions
│   └── cli.py              # CLI entry point
│
└── elt_llm_<name>/         # Document-specific modules (examples)
    ├── elt_llm_dama/       # DAMA-DMBOK
    ├── elt_llm_sad/        # SAD (future)
    ├── elt_llm_leanix/     # LeanIX (future)
    └── elt_llm_supplier/   # Supplier docs (future)
```

## Package Responsibilities

| Package | Purpose | Dependencies |
|---------|---------|--------------|
| `elt_llm_core` | Shared RAG infrastructure | `chromadb`, `llama-index`, `ollama` |
| `elt_llm_ingest` | Generic document ingestion | `elt_llm_core` |
| `elt_llm_query` | Query interface | `elt_llm_core` |
| `elt_llm_dama` | DAMA-DMBOK specific | `elt_llm_core`, `elt_llm_ingest`, `elt_llm_query` |

## Configuration Pattern

Each document-specific module has two config files:

### `config/rag_config.yaml` - Shared RAG Settings

```yaml
# ChromaDB settings
chroma:
  persist_dir: "./chroma_db"
  tenant: "rag_tenants"
  database: "knowledge_base"

# Ollama settings
ollama:
  base_url: "http://localhost:11434"
  embedding_model: "nomic-embed-text"
  llm_model: "llama3.2"

# Chunking settings
chunking:
  strategy: "sentence"
  chunk_size: 1024
  chunk_overlap: 200

# Query settings
query:
  similarity_top_k: 5
  system_prompt: |
    You are a helpful assistant...
```

### `config/ingest_config.yaml` - Document-Specific Settings

```yaml
collection_name: "dama_dmbok"

file_paths:
  - "~/Documents/__data/books/DAMA-DMBOK2R_unlocked.pdf"

metadata:
  domain: "data_management"
  type: "body_of_knowledge"

rebuild: true
```

## Usage

### elt_llm_dama (Example)

#### Ingest DAMA-DMBOK

```bash
cd elt_llm_dama
uv sync

# Ingest documents
elt-llm-dama-ingest

# Or
uv run python -m elt_llm_dama.ingest
```

#### Query DAMA-DMBOK

```bash
# Interactive mode
elt-llm-dama-query

# Single query
elt-llm-dama-query --query "What is data governance?"
```

### Using Generic Modules Directly

#### Ingest with `elt_llm_ingest`

```bash
elt-llm-ingest --config path/to/ingest_config.yaml
```

#### Query with `elt_llm_query`

```bash
elt-llm-query --config path/to/rag_config.yaml --collection dama_dmbok
```

## Creating a New Document Module

To add a new document type (e.g., `elt_llm_sad`):

### 1. Create Directory Structure

```bash
mkdir -p elt_llm_sad/src/elt_llm_sad
mkdir -p elt_llm_sad/config
mkdir -p elt_llm_sad/tests
```

### 2. Create `pyproject.toml`

```toml
[project]
name = "elt-llm-sad"
version = "0.1.0"
description = "SAD RAG module"
requires-python = ">=3.11,<3.14"
dependencies = [
    "elt-llm-core>=0.1.0",
    "elt-llm-ingest>=0.1.0",
    "elt-llm-query>=0.1.0",
]
```

### 3. Create Config Files

**`config/rag_config.yaml`:**
```yaml
chroma:
  persist_dir: "./chroma_db"
  tenant: "rag_tenants"
  database: "knowledge_base"

ollama:
  base_url: "http://localhost:11434"
  embedding_model: "nomic-embed-text"
  llm_model: "llama3.2"

chunking:
  strategy: "sentence"
  chunk_size: 1024
  chunk_overlap: 200
```

**`config/ingest_config.yaml`:**
```yaml
collection_name: "sad"

file_paths:
  - "~/Documents/__data/books/SAD.pdf"

metadata:
  domain: "architecture"
  type: "handbook"

rebuild: true
```

### 4. Create CLI Wrapper

**`src/elt_llm_sad/cli.py`:**
```python
from elt_llm_dama.cli import ingest_main, query_main

# Reuse the same pattern
ingest_main = ingest_main
query_main = query_main
```

Or copy the pattern from `elt_llm_dama`.

### 5. Update Root `pyproject.toml`

Add to `[tool.uv.workspace]`:
```toml
"elt_llm_sad",
```

Add to `[tool.uv.sources]`:
```toml
elt-llm-sad = { workspace = true }
```

### 6. Sync and Ingest

```bash
cd elt_lake
uv sync

cd elt_llm_sad
uv sync
elt-llm-sad-ingest
```

## Python Version Constraint

**Important:** ChromaDB is not yet compatible with Python 3.14.

All LLM RAG packages require: `Python >=3.11, <3.14`

### Workspace Conflict

Your workspace has mixed Python version requirements:
- LLM RAG packages: `>=3.11, <3.14`
- Some other packages: `>=3.14`

**Solutions:**

1. **Use Python 3.12 or 3.13** for the entire workspace (recommended)
   - Update packages with `>=3.14` to `>=3.11,<3.14`

2. **Use separate virtual environments**
   - One for LLM RAG packages (Python 3.12/3.13)
   - One for other packages (Python 3.14)

3. **Wait for ChromaDB Python 3.14 support**
   - Track at: https://github.com/chroma-core/chroma/issues

## Prerequisites

- Python 3.11, 3.12, or 3.13
- Ollama running locally: `ollama serve`
- Required models:
  ```bash
  ollama pull nomic-embed-text
  ollama pull llama3.2
  ```

## Architecture

```
┌─────────────────────────────────────────┐
│  config/rag_config.yaml                 │
│  config/ingest_config.yaml              │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│         elt_llm_dama                    │
│  (or elt_llm_sad, elt_llm_leanix...)    │
│  - CLI wrappers                         │
│  - Document-specific config             │
└─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ elt_llm_core │ │elt_llm_ingest│ │ elt_llm_query│
│ - ChromaDB   │ │ - Loading    │ │ - Retrieval  │
│ - Ollama     │ │ - Chunking   │ │ - Querying   │
│ - Config     │ │ - Indexing   │ │ - Response   │
└──────────────┘ └──────────────┘ └──────────────┘
```

## Migration from elt_doc_damabok

The original `elt_doc_damabok` module can be:

1. **Kept as-is** for simple character-based chunking
2. **Migrated** to use `elt_llm_dama` for LlamaIndex-based chunking
3. **Deprecated** in favor of the new modular structure

To migrate:
1. Update file paths in `elt_llm_dama/config/ingest_config.yaml`
2. Run `elt-llm-dama-ingest` to build the new index
3. Use `elt-llm-dama-query` for querying
