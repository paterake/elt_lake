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

The models required by this module are listed in:

- `elt_doc_damabok/config/ollama.json` (`models` field)

You can pull them using those names, for example:

```bash
cd elt_doc_damabok
for m in $(jq -r '.models[]' config/ollama.json); do
  ollama pull "$m"
done
```

## Python environment (uv)

From the repository root:

```bash
cd elt_doc_damabok
uv sync
```

This creates and manages an isolated virtual environment for this module and
installs only the dependencies declared in `pyproject.toml`.

No global `pip` installs are needed; everything stays inside the `uv`-managed
environment.

## Config

Configuration lives in:

- `elt_doc_damabok/config/doc_damabok.json` (document and chunking)
- `elt_doc_damabok/config/vector_db.json` (vector store and models)
- `elt_doc_damabok/config/ollama.json` (models, system prompt, test question)

See `ARCHITECTURE.md` for field-level details and how these files are used by
the ingestion, query, and initialisation pipelines.

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
- embed each chunk via the embedding model configured in `vector_db.json`
- store embeddings and chunks in a persistent Chroma collection as
  configured in `vector_db.json`

You only need to re-run this if the PDF or configuration changes.

## Querying the DMBOK locally

After ingestion, you can run interactive Q&A against the DMBOK:

```bash
cd elt_doc_damabok
uv run python -m elt_doc_damabok.query
```

This will:

- connect to the existing Chroma index
- embed your question with the configured embedding model
- retrieve the most relevant DMBOK chunks
- build a prompt containing those excerpts and your question
- call the configured LLM via Ollama to produce an answer

The answers are grounded in the DMBOK text stored in the index.

## One-shot initialisation

To validate and initialise everything in one step:

```bash
cd elt_doc_damabok
uv run python -m elt_doc_damabok.initialise
```

This will:

- verify the DMBOK PDF path
- verify connectivity to the Ollama server
- ensure required Ollama models are present (pulling them if needed)
- build or rebuild the Chroma index
- verify that the index contains documents
- run a single test question against the DMBOK index and print the answer

After this completes successfully, the module is ready for regular use via the
`ingest` and `query` commands above.

## Notes and limitations

- If the PDF is image-based or poorly OCRed, `pypdf` may produce low-quality
  text. In that case, consider pre-processing the PDF with OCR and updating
  `source_pdf` to point at the cleaned version.
- All computation happens locally: embeddings, vector search, and LLM
  inference are performed on your Mac using Ollama and the `uv`-managed
  environment for Python dependencies.
