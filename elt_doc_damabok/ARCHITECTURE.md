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
  - `config/ollama.json`
     - List of Ollama models that must be available.
     - A test question used to validate the RAG setup.

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
- `chunking_strategy`: the chunking approach in use. Currently only `"page"`
  is supported — each page is chunked independently; chunks do not span page
  boundaries. Validated at initialisation.

### `vector_db.json`

Defines the **vector database and retrieval** configuration:

- `provider`: currently `"chroma"`.
- `chroma.persist_dir`: directory for Chroma persistence on disk.
- `chroma.collection_name`: logical name of the collection, e.g. `"damabok"`.
- `embedding_model`: embedding model name for Ollama (e.g. `nomic-embed-text`).
- `llm_model`: LLM name for Ollama (e.g. `llama3.1:8b`).
- `top_k`: number of chunks to retrieve per query.
- `max_prompt_chars`: soft cap on prompt size in characters.

The ingestion and query pipelines read `doc_damabok.json` for document and
chunking settings, and `vector_db.json` for vector-store and model settings.

### `ollama.json`

Defines the **Ollama-specific** configuration:

- `models`: list of Ollama model names that must be installed (for example
  `nomic-embed-text:latest` and `llama3.1:8b`).
- `system_prompt`: the LLM instruction text prepended to every RAG prompt,
  defining the assistant's role and constraints.
- `test_question`: a single question used by the initialisation process to
  validate that retrieval and generation are functioning correctly.

The initialisation and query pipelines use this to drive model checks,
prompt construction, and smoke-test queries.

## Ingestion flow

Code: `elt_doc_damabok/src/elt_doc_damabok/ingest.py`

Steps:

1. **Config load**
   - `load_doc_config()` reads `doc_damabok.json`.
   - `load_vector_config()` reads `vector_db.json`.
2. **Paths and parameters**
   - `source_pdf` is expanded and resolved.
   - `chunk_size` and `chunk_overlap` are applied.
   - `embedding_model` is taken from `vector_db.json`.
   - Chroma `persist_dir` and `collection_name` are derived from
     `vector_db.json`.
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

## Initialisation flow

Code: `elt_doc_damabok/src/elt_doc_damabok/initialise.py`

Steps:

1. **Config load**
   - Reads `doc_damabok.json`, `vector_db.json`, and `ollama.json`.
2. **RAG config validation**
   - Asserts `chunking_strategy` is a supported value (`"page"`).
   - Asserts `chunk_overlap` < `chunk_size` (prevents infinite chunking loop).
   - Asserts `top_k × chunk_size` ≤ `max_prompt_chars` (ensures retrieved
     chunks fit within the configured prompt budget without silent truncation).
3. **Prerequisite checks**
   - Verifies the DMBOK PDF path exists.
   - Verifies connectivity to the Ollama server.
   - Ensures required Ollama models listed in `models` are
     installed, pulling them if needed.
4. **Vector store parameters**
   - Resolves Chroma persistence directory, collection name, embedding model,
     LLM model, `top_k`, and `max_prompt_chars` from `vector_db.json`.
5. **Ingestion**
   - Calls the ingestion pipeline to (re)build the Chroma index.
6. **Index verification**
   - Confirms that the Chroma collection contains at least one document.
7. **RAG smoke test**
   - Runs a single query using the configured test question.
   - Embeds the question, retrieves the top `top_k` chunks, builds a prompt,
     and calls the LLM to produce an answer printed to the console.

This flow validates the end-to-end setup so the module is ready for regular
interactive use.

## Query flow

Code: `elt_doc_damabok/src/elt_doc_damabok/query.py`

Steps:

1. **Config load**
   - `load_vector_config()` reads `vector_db.json`.
   - `load_ollama_config()` reads `ollama.json`.
   - Resolves `embedding_model`, `llm_model`, Chroma directory and collection
     name, `top_k`, `max_prompt_chars`, and `system_prompt`.
2. **Vector store connect**
   - Creates a persistent Chroma client and opens the configured collection.
3. **Interactive loop**
   - Reads a natural-language question from stdin.
   - Embeds it via `ollama.embeddings` using the same embedding model as
     ingestion.
   - Queries Chroma with the question embedding, requesting `top_k` nearest
     neighbours.
4. **Prompt construction**
   - `build_prompt()` formats the retrieved documents as numbered excerpts.
   - Applies the configured `system_prompt`.
   - Enforces `max_prompt_chars` to keep the prompt within a safe size.
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
