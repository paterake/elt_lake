from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings
from pypdf import PdfReader

import ollama


def _load_config() -> dict[str, Any]:
    here = Path(__file__).resolve().parent.parent.parent
    cfg_path = here / "config" / "doc_damabok.json"
    with cfg_path.open() as f:
        return json.load(f)


def _expand_path(path_str: str) -> Path:
    return Path(os.path.expanduser(path_str)).resolve()


def _load_vector_config() -> dict[str, Any]:
    here = Path(__file__).resolve().parent.parent.parent
    cfg_path = here / "config" / "vector_db.json"
    with cfg_path.open() as f:
        return json.load(f)


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
        embeddings.append(resp["embedding"])
    return embeddings


def build_index() -> None:
    cfg = _load_config()
    vcfg = _load_vector_config()
    pdf_path = _expand_path(cfg["source_pdf"])
    chunk_size = int(cfg.get("chunk_size", 1200))
    chunk_overlap = int(cfg.get("chunk_overlap", 200))
    embed_model = str(
        vcfg.get(
            "embedding_model",
            cfg.get("ollama_embed", "nomic-embed-text"),
        )
    )
    chroma_cfg = vcfg.get("chroma", {})
    persist_dir = _expand_path(
        chroma_cfg.get(
            "persist_dir",
            cfg.get("chroma_persist_dir", "./damabok_chroma"),
        )
    )
    collection_name = str(chroma_cfg.get("collection_name", "damabok"))

    persist_dir.mkdir(parents=True, exist_ok=True)

    pages = _extract_pages(pdf_path)
    chunks = _chunk_pages(pages, max_chars=chunk_size, overlap=chunk_overlap)

    client = chromadb.Client(
        Settings(
            is_persistent=True,
            persist_directory=str(persist_dir),
        )
    )
    collection = client.get_or_create_collection(collection_name)

    existing = collection.count()
    if existing:
        collection.delete(where={})

    embeddings = _embed_texts(chunks, model=embed_model)

    ids = [f"chunk-{i}" for i in range(len(chunks))]
    collection.add(ids=ids, embeddings=embeddings, documents=chunks)


def main() -> None:
    build_index()


if __name__ == "__main__":
    main()
