from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import chromadb
from pypdf import PdfReader

import ollama


def _load_config() -> dict[str, Any]:
    here = Path(__file__).resolve().parent.parent.parent
    cfg_path = here / "config" / "doc_damabok.json"
    try:
        with cfg_path.open() as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {cfg_path}")


def _expand_path(path_str: str) -> Path:
    return Path(os.path.expanduser(path_str)).resolve()


def _load_vector_config() -> dict[str, Any]:
    here = Path(__file__).resolve().parent.parent.parent
    cfg_path = here / "config" / "vector_db.json"
    try:
        with cfg_path.open() as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {cfg_path}")


def _extract_pages(pdf_path: Path) -> list[str]:
    reader = PdfReader(str(pdf_path))
    pages: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text:
            pages.append(" ".join(text.split()))
    return pages


def _chunk_pages(pages: list[str], max_chars: int, overlap: int) -> list[str]:
    chunks: list[str] = []
    for page in pages:
        start = 0
        while start < len(page):
            end = start + max_chars
            chunk = page[start:end]
            if chunk.strip():
                chunks.append(chunk)
            if end >= len(page):
                break
            start = end - overlap
    return chunks


def _embed_texts(texts: list[str], model: str) -> list[list[float]]:
    embeddings: list[list[float]] = []
    for t in texts:
        resp = ollama.embeddings(model=model, prompt=t)
        embeddings.append(resp.embedding)
    return embeddings


def build_index() -> None:
    cfg = _load_config()
    vcfg = _load_vector_config()
    pdf_path = _expand_path(cfg["source_pdf"])
    chunk_size = int(cfg["chunk_size"])
    chunk_overlap = int(cfg["chunk_overlap"])
    embed_model = str(vcfg["embedding_model"])
    chroma_cfg = vcfg.get("chroma", {})
    persist_dir = _expand_path(
        chroma_cfg["persist_dir"]
    )
    collection_name = str(chroma_cfg["collection_name"])

    persist_dir.mkdir(parents=True, exist_ok=True)

    pages = _extract_pages(pdf_path)
    chunks = _chunk_pages(pages, max_chars=chunk_size, overlap=chunk_overlap)

    client = chromadb.PersistentClient(path=str(persist_dir))

    # Delete and recreate collection to ensure clean index (ignore if not yet created)
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass
    collection = client.get_or_create_collection(collection_name)

    embeddings = _embed_texts(chunks, model=embed_model)

    ids = [f"chunk-{i}" for i in range(len(chunks))]
    collection.add(ids=ids, embeddings=embeddings, documents=chunks)


def main() -> None:
    build_index()


if __name__ == "__main__":
    main()
