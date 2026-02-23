# RAG Packages Setup Summary

## Created Packages

Two new workspace packages have been created for scalable multi-document RAG:

### 1. `elt_llm_rag` - Core RAG Infrastructure

**Purpose:** LlamaIndex + Chroma + Ollama integration

**Features:**
- Multi-format document loading (PDF, DOCX, TXT, HTML, etc.)
- Sentence-aware and semantic chunking strategies
- ChromaDB vector storage with named collections
- Ollama-based embeddings and LLM inference

**Location:** `elt_llm_rag/`

**CLI Commands:**
```bash
uv run python -m elt_llm_rag.ingest --config config.json
uv run python -m elt_llm_rag.query --config config.json
```

### 2. `elt_doc_rag` - Document Collection Management

**Purpose:** Configuration-driven multi-collection management

**Features:**
- YAML configuration for multiple document collections
- Per-collection chunking and metadata settings
- Status diagnostics for all collections
- Collection-scoped ingestion and querying

**Location:** `elt_doc_rag/`

**CLI Commands:**
```bash
uv run python -m elt_doc_rag.status --config config/documents.yaml
uv run python -m elt_doc_rag.ingest --config config/documents.yaml
uv run python -m elt_doc_rag.query --config config/documents.yaml --collection dama_dmbok
```

## Configuration Example

**File:** `elt_doc_rag/config/documents.yaml`

```yaml
collections:
  - name: dama_dmbok
    display_name: "DAMA-DMBOK2 Data Management"
    file_paths:
      - "~/Documents/__data/books/DAMA-DMBOK2R_unlocked.pdf"
    chunk_size: 1024
    chunk_overlap: 200

  - name: fa_handbook
    display_name: "Financial Accounting Handbook"
    file_paths:
      - "~/Documents/__data/books/FA_Handbook.pdf"
    chunk_size: 1024
    chunk_overlap: 200

persist_dir: "./chroma_db"
embedding_model: "nomic-embed-text"
llm_model: "llama3.2"
```

## Python Version Constraint

**Important:** ChromaDB is not yet compatible with Python 3.14 due to pydantic v1 issues.

The new packages require: `Python >=3.11, <3.14`

Your workspace has mixed Python version requirements:
- Some packages require `>=3.14`
- RAG packages require `>=3.11, <3.14`

**Solutions:**

1. **Use Python 3.12 or 3.13** for the entire workspace (recommended)
2. **Use separate virtual environments** for RAG vs other packages
3. **Wait for ChromaDB Python 3.14 support** (track at: https://github.com/chroma-core/chroma/issues)

## Quick Start

### 1. Ensure Python 3.11-3.13

```bash
python --version  # Should be 3.11, 3.12, or 3.13
```

### 2. Install Ollama Models

```bash
ollama pull nomic-embed-text
ollama pull llama3.2
```

### 3. Update Configuration

Edit `elt_doc_rag/config/documents.yaml` with your actual file paths.

### 4. Check Status

```bash
cd elt_doc_rag
uv run python -m elt_doc_rag.status --config config/documents.yaml
```

### 5. Ingest Collections

```bash
uv run python -m elt_doc_rag.ingest --config config/documents.yaml
```

### 6. Query Collections

```bash
# Interactive mode
uv run python -m elt_doc_rag.query \
  --config config/documents.yaml \
  --collection dama_dmbok

# Single query
uv run python -m elt_doc_rag.query \
  --config config/documents.yaml \
  --collection dama_dmbok \
  --query "What is data governance?"
```

## Architecture

```
┌─────────────────────────────────────┐
│     documents.yaml (config)         │
│  - Multiple collections defined     │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│         elt_doc_rag                 │
│  - config.py  (YAML parsing)        │
│  - ingest.py (multi-collection)     │
│  - query.py  (collection-scoped)    │
│  - status.py (diagnostics)          │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│         elt_llm_rag                 │
│  - LlamaIndex core                  │
│  - ChromaDB integration             │
│  - Ollama embeddings/LLM            │
└─────────────────────────────────────┘
```

## Migration from elt_doc_damabok

The original `elt_doc_damabok` module uses simple character-based chunking with `pypdf`.

**To migrate:**

1. Keep using `elt_doc_damabok` for simple PDF-only use cases
2. Use `elt_doc_rag` for:
   - Multiple documents/books
   - Multi-format support (DOCX, HTML, etc.)
   - Better chunking (sentence-aware)
   - Collection management

3. Point `elt_doc_rag/config/documents.yaml` to your existing PDF paths
4. Re-run ingestion to build new indices with LlamaIndex

## Adding New Collections

1. Add to `documents.yaml`:
   ```yaml
   collections:
     - name: my_new_book
       display_name: "My Book"
       file_paths:
         - "~/path/to/book.pdf"
   ```

2. Ingest:
   ```bash
   uv run python -m elt_doc_rag.ingest \
     --config config/documents.yaml \
     --collection my_new_book
   ```

3. Query:
   ```bash
   uv run python -m elt_doc_rag.query \
     --config config/documents.yaml \
     --collection my_new_book
   ```

## Tests

Run tests for the configuration module:

```bash
cd elt_doc_rag
uv run pytest tests/ -v
```

## Next Steps

1. **Update file paths** in `elt_doc_rag/config/documents.yaml`
2. **Ensure Ollama is running**: `ollama serve`
3. **Pull required models** if not already done
4. **Run ingestion** for your collections
5. **Test querying** with sample questions
