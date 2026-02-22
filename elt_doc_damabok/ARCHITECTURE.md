# elt-doc-damabok Architecture

This module provides a local Retrieval-Augmented Generation (RAG) setup over
the DAMA-DMBOK2R manual using Ollama-hosted models and a Chroma vector store.

The core idea:

- The DMBOK PDF is treated as a knowledge source.
- Text is extracted, chunked, embedded, and stored in a local vector database.
- At query time, relevant chunks are retrieved and sent to a local LLM that
  generates answers grounded in those excerpts.

There is **no model fine-tuning**; all behaviour is driven by retrieval and
prompting.

## High-level components

- **Configuration**
  - `config/doc_damabok.json`
    - Path to the DMBOK PDF.
    - Chunking parameters (`chunk_size`, `chunk_overlap`).
  - `config/vector_db.json`
    - Vector DB provider and parameters.
    - Embedding model and LLM model names.
    - Retrieval parameters such as `top_k`.

- **Ingestion pipeline**
  - `src/elt_doc_damabok/ingest.py`
    - Reads configuration.
    - Extracts text from the DMBOK PDF.
    - Splits text into overlapping chunks.
    - Embeds each chunk using Ollama.
    - Stores embeddings and documents in a persistent Chroma collection.

- **Query pipeline**
  - `src/elt_doc_damabok/query.py`
    - Loads the existing Chroma index.
    - Embeds user questions using the same embedding model.
    - Retrieves the most similar chunks from Chroma.
    - Constructs a prompt containing those excerpts and the question.
    - Calls the local LLM via Ollama to produce an answer.

## Configuration model

### `doc_damabok.json`

Defines the **document-level** configuration:

- `source_pdf`: path to the DMBOK PDF.
- `chunk_size`: maximum characters per text chunk.
- `chunk_overlap`: overlap between consecutive chunks to preserve context.

### `vector_db.json`

Defines the **vector database and retrieval** configuration:

- `provider`: currently `"chroma"`.
- `chroma.persist_dir`: directory for Chroma persistence on disk.
- `chroma.collection_name`: logical name of the collection, e.g. `"damabok"`.
- `embedding_model`: embedding model name for Ollama (e.g. `nomic-embed-text`).
- `llm_model`: LLM name for Ollama (e.g. `llama3.1:8b`).
- `top_k`: number of chunks to retrieve per query.

The ingestion and query pipelines read `doc_damabok.json` for document and
chunking settings, and `vector_db.json` for vector-store and model settings.

## Ingestion flow

Code: `elt_doc_damabok/src/elt_doc_damabok/ingest.py`

Steps:

1. **Config load**
   - `_load_config()` reads `doc_damabok.json`.
   - `_load_vector_config()` reads `vector_db.json`.
2. **Paths and parameters**
   - `source_pdf` is expanded and resolved.
   - `chunk_size` and `chunk_overlap` are applied.
   - `embedding_model` is taken from `vector_db.json` (or fallback).
   - Chroma `persist_dir` and `collection_name` are derived from
     `vector_db.json` (or fallback).
3. **Text extraction**
   - `_extract_pages()` uses `pypdf.PdfReader` to extract text per page and
     normalise whitespace.
4. **Chunking**
   - `_chunk_pages()` slices page text into overlapping character windows.
   - Produces a sequence of chunks that preserve local context.
5. **Embedding**
   - `_embed_texts()` iterates over chunks and calls `ollama.embeddings` with
     the configured embedding model.
6. **Vector store write**
   - A persistent Chroma client is created using the configured directory.
   - The target collection is obtained or created.
   - Existing entries are cleared.
   - New embeddings and documents are added with stable IDs (`chunk-<index>`).

The result is a local, persistent index of DMBOK text chunks keyed by dense
embeddings.

## Query flow

Code: `elt_doc_damabok/src/elt_doc_damabok/query.py`

Steps:

1. **Config load**
   - `_load_config()` reads `doc_damabok.json`.
   - `_load_vector_config()` reads `vector_db.json`.
   - Resolves `embedding_model`, `llm_model`, Chroma directory and collection
     name, and `top_k`.
2. **Vector store connect**
   - Creates a persistent Chroma client and opens the configured collection.
3. **Interactive loop**
   - Reads a natural-language question from stdin.
   - Embeds it via `ollama.embeddings` using the same embedding model as
     ingestion.
   - Queries Chroma with the question embedding, requesting `top_k` nearest
     neighbours.
4. **Prompt construction**
   - `_build_prompt()` formats the retrieved documents as numbered excerpts.
   - Appends the user question and an instruction to answer only from the
     excerpts.
5. **LLM call**
   - Sends the prompt to Ollama via `ollama.chat` using `llm_model`.
   - Streams or returns the model’s answer to the console.

This ensures answers are grounded in the DMBOK excerpts selected by the vector
search.

## External dependencies and runtime

- **Ollama**
  - Hosts:
    - The LLM: `llama3.1:8b` (or configured alternative).
    - The embedding model: `nomic-embed-text`.
  - The Python code communicates via the `ollama` SDK.

- **Chroma**
  - Local vector database, persisted on disk.
  - Stores embeddings and the corresponding text chunks.
  - Provides nearest-neighbour search for retrieval.

- **pypdf**
  - Extracts text from the DMBOK PDF.

- **uv-managed Python environment**
  - All dependencies are declared in `pyproject.toml`.
  - `uv sync` creates an isolated environment for this module.

## Extensibility

The architecture is designed to be extensible:

- Swapping the embedding model or LLM:
  - Change names in `vector_db.json`, rerun ingestion (for embeddings) if
    necessary.
- Changing vector store:
  - `provider` in `vector_db.json` provides a hook for future backends
    (e.g. another local DB or a remote service).
- Supporting additional documents:
  - Additional PDFs or data sources could be ingested into separate collections
    or the same one with appropriate metadata.
