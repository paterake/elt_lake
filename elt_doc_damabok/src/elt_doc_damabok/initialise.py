from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import chromadb
import ollama

from elt_doc_damabok.ingest import (
    build_index,
    _expand_path as expand_path,
    _load_config as load_doc_config,
    _load_vector_config as load_vector_config,
)
from elt_doc_damabok.query import _build_prompt, _embed_query


def _load_ollama_config() -> dict[str, Any]:
    here = Path(__file__).resolve().parent.parent.parent
    cfg_path = here / "config" / "ollama.json"
    try:
        with cfg_path.open() as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {cfg_path}")


def _ensure_pdf_exists(doc_cfg: dict[str, Any]) -> Path:
    pdf_path = expand_path(doc_cfg["source_pdf"])
    if not pdf_path.is_file():
        raise RuntimeError(f"DMBOK PDF not found at {pdf_path}")
    return pdf_path


def _ensure_ollama_server() -> None:
    try:
        ollama.list()
    except Exception as exc:
        raise RuntimeError("Unable to reach Ollama server. Ensure `ollama serve` is running.") from exc


def _ensure_models_installed(ocfg: dict[str, Any]) -> None:
    models_cfg = ocfg.get("models") or []
    if not isinstance(models_cfg, list) or not models_cfg:
        raise RuntimeError("No models defined in ollama config.")
    names: set[str] = {str(m) for m in models_cfg}
    listed = ollama.list()
    installed = {m.model.removesuffix(":latest") for m in listed.models}
    for model in names:
        if model.removesuffix(":latest") not in installed:
            for _ in ollama.pull(model=model):
                pass
    listed_after = ollama.list()
    installed_after = {m.model.removesuffix(":latest") for m in listed_after.models}
    missing = [m for m in names if m.removesuffix(":latest") not in installed_after]
    if missing:
        raise RuntimeError(f"Models not available after pull: {missing}")


def _vector_store_params(vcfg: dict[str, Any]) -> tuple[Path, str, int, str, str]:
    chroma_cfg = vcfg.get("chroma", {})
    persist_dir_str = chroma_cfg.get("persist_dir", "./damabok_chroma")
    persist_dir = expand_path(persist_dir_str)
    collection_name = str(chroma_cfg.get("collection_name", "damabok"))
    embed_model = vcfg.get("embedding_model") or ""
    llm_model = vcfg.get("llm_model") or ""
    if not embed_model or not llm_model:
        raise RuntimeError("embedding_model and llm_model must be set in vector_db config.")
    top_k = int(vcfg.get("top_k", 5))
    return persist_dir, collection_name, top_k, embed_model, llm_model


def _verify_index(persist_dir: Path, collection_name: str) -> int:
    client = chromadb.PersistentClient(path=str(persist_dir))
    collection = client.get_or_create_collection(collection_name)
    return collection.count()


def _test_rag(
    question: str,
    persist_dir: Path,
    collection_name: str,
    top_k: int,
    embed_model: str,
    llm_model: str,
) -> str:
    client = chromadb.PersistentClient(path=str(persist_dir))
    collection = client.get_or_create_collection(collection_name)
    q_emb = _embed_query(question, model=embed_model)
    results = collection.query(query_embeddings=[q_emb], n_results=top_k)
    docs = results.get("documents") or [[]]
    contexts = docs[0] if docs else []
    prompt = _build_prompt(question, contexts)
    resp = ollama.chat(model=llm_model, messages=[{"role": "user", "content": prompt}])
    return resp.message.content


def initialise() -> None:
    doc_cfg = load_doc_config()
    vcfg = load_vector_config()
    ocfg = _load_ollama_config()

    pdf_path = _ensure_pdf_exists(doc_cfg)
    _ensure_ollama_server()
    _ensure_models_installed(ocfg)

    persist_dir, collection_name, top_k, embed_model, llm_model = _vector_store_params(vcfg)
    persist_dir.mkdir(parents=True, exist_ok=True)

    build_index()

    count = _verify_index(persist_dir, collection_name)
    if count == 0:
        raise RuntimeError("Chroma index is empty after ingestion.")

    question = str(ocfg["test_question"])
    answer = _test_rag(
        question=question,
        persist_dir=persist_dir,
        collection_name=collection_name,
        top_k=top_k,
        embed_model=embed_model,
        llm_model=llm_model,
    )

    print(f"DMBOK PDF found at: {pdf_path}")
    print(f"Chroma index directory: {persist_dir}")
    print(f"Chroma collection: {collection_name} (documents: {count})")
    print("Test question:")
    print(question)
    print("Test answer:")
    print(answer)


def main() -> None:
    initialise()


if __name__ == "__main__":
    main()
