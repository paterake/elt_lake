from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import chromadb

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


def _embed_query(query: str, model: str) -> list[float]:
    resp = ollama.embeddings(model=model, prompt=query)
    return resp.embedding


def _build_prompt(question: str, contexts: list[str]) -> str:
    parts: list[str] = [
        "You are an assistant answering questions about the DAMA-DMBOK2R data management body of knowledge.",
        "Use only the information in the provided excerpts.",
        "If the answer is not clearly supported, say you cannot answer from the book.",
        "",
    ]
    for i, c in enumerate(contexts, start=1):
        parts.append(f"Excerpt {i}:")
        parts.append(c)
        parts.append("")
    parts.append(f"Question: {question}")
    parts.append("Answer:")
    return "\n".join(parts)


def interactive_qa() -> None:
    vcfg = _load_vector_config()
    embed_model = str(vcfg["embedding_model"])
    llm_model = str(vcfg["llm_model"])
    chroma_cfg = vcfg.get("chroma", {})
    persist_dir = _expand_path(
        chroma_cfg.get(
            "persist_dir",
            "./damabok_chroma",
        )
    )
    collection_name = str(chroma_cfg.get("collection_name", "damabok"))
    top_k = int(vcfg.get("top_k", 5))

    client = chromadb.PersistentClient(path=str(persist_dir))
    collection = client.get_or_create_collection(collection_name)

    while True:
        try:
            q = input("DMBOK question (or 'quit'): ").strip()
        except EOFError:
            break
        if not q or q.lower() in {"quit", "exit"}:
            break

        q_emb = _embed_query(q, model=embed_model)
        results = collection.query(query_embeddings=[q_emb], n_results=top_k)
        docs = results.get("documents") or [[]]
        contexts = docs[0] if docs else []

        prompt = _build_prompt(q, contexts)
        resp = ollama.chat(model=llm_model, messages=[{"role": "user", "content": prompt}])
        print("\n--- Answer ---\n")
        print(resp.message.content)
        print("\n-------------\n")


def main() -> None:
    interactive_qa()


if __name__ == "__main__":
    main()
