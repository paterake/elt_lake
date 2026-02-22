# elt-doc-damabok

ELT-style module for working with the **DAMA-DMBOK2R** manual using a local
Retrieval-Augmented Generation (RAG) setup on top of Ollama.

This does **not** fine-tune any model. Instead, it:

- extracts text from the DMBOK PDF
- chunks it into overlapping passages
- embeds those passages with a local embedding model
- stores them in a local Chroma vector index
- uses a local LLM to answer questions grounded in the retrieved excerpts

## Prerequisites

- macOS with Ollama installed and running
- Python managed via `uv` (no global `pip` installs)
- DMBOK PDF available at:

  ```text
  ~/Documents/__data/books/DAMA-DMBOK2R_unlocked.pdf
  ```

If your PDF is elsewhere, update:

- `elt_doc_damabok/config/doc_damabok.json`

## Ollama models to pull

Run these once:

```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

- `llama3.1:8b` is used as the answering model.
- `nomic-embed-text` is used to embed DMBOK text chunks and user questions.

## Python environment (uv)

From the repository root:

```bash
cd elt_doc_damabok
uv sync
```

This creates and manages an isolated virtual environment for this module and
installs only the dependencies declared in `pyproject.toml`:

- `pypdf` for PDF text extraction
- `chromadb` for the local vector database
- `numpy` for numeric operations
- `ollama` for talking to the local Ollama server

No global `pip` installs are needed; everything stays inside the `uv`-managed
environment.

## Config

Configuration lives in:

- `elt_doc_damabok/config/doc_damabok.json` (document and chunking)
- `elt_doc_damabok/config/vector_db.json` (vector store and models)

See `ARCHITECTURE.md` for field-level details and how these files are used by
the ingestion and query pipelines.

## One-time ingestion (build the index)

First, make sure Ollama is running:

```bash
ollama serve
```

Then, from the repository root:

```bash
cd elt_doc_damabok
uv run python -m elt_doc_damabok.ingest
```

This will:

- load the DMBOK PDF
- extract and clean page text
- chunk it according to `chunk_size` / `chunk_overlap`
- embed each chunk via `nomic-embed-text`
- store embeddings and chunks in a persistent Chroma collection called
  `damabok` at `chroma_persist_dir`

You only need to re-run this if the PDF or configuration changes.

## Querying the DMBOK locally

After ingestion, you can run interactive Q&A against the DMBOK:

```bash
cd elt_doc_damabok
uv run python -m elt_doc_damabok.query
```

This will:

- connect to the existing Chroma index
- embed your question with `nomic-embed-text`
- retrieve the most relevant DMBOK chunks
- build a prompt containing those excerpts and your question
- call `llama3.1:8b` via Ollama to produce an answer

The answers are grounded in the DMBOK text stored in the index.

## Notes and limitations

- If the PDF is image-based or poorly OCRed, `pypdf` may produce low-quality
  text. In that case, consider pre-processing the PDF with OCR and updating
  `source_pdf` to point at the cleaned version.
- All computation happens locally: embeddings, vector search, and LLM
  inference are performed on your Mac using Ollama and the `uv`-managed
  environment for Python dependencies.
