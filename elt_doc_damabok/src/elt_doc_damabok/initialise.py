from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb
import ollama

from elt_doc_damabok.ingest import build_index
from elt_doc_damabok.utils import (
    build_prompt,
    embed_query,
    expand_path,
    load_doc_config,
    load_ollama_config,
    load_vector_config,
)


_SUPPORTED_CHUNKING_STRATEGIES = {"page"}


def _validate_rag_config(doc_cfg: dict[str, Any], vcfg: dict[str, Any]) -> None:
    chunk_size = int(doc_cfg["chunk_size"])
    chunk_overlap = int(doc_cfg["chunk_overlap"])
    chunking_strategy = str(doc_cfg["chunking_strategy"])
    top_k = int(vcfg["top_k"])
    max_prompt_chars = int(vcfg["max_prompt_chars"])

    if chunking_strategy not in _SUPPORTED_CHUNKING_STRATEGIES:
        raise RuntimeError(
            f"Unsupported chunking_strategy '{chunking_strategy}'. "
            f"Supported: {sorted(_SUPPORTED_CHUNKING_STRATEGIES)}"
        )
    if chunk_overlap >= chunk_size:
        raise RuntimeError(
            f"chunk_overlap ({chunk_overlap}) must be less than chunk_size ({chunk_size})."
        )
    if top_k * chunk_size > max_prompt_chars:
        raise RuntimeError(
            f"top_k ({top_k}) × chunk_size ({chunk_size}) = {top_k * chunk_size} chars "
            f"exceeds max_prompt_chars ({max_prompt_chars}). "
            f"Reduce top_k or chunk_size, or increase max_prompt_chars."
        )


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


def _vector_store_params(vcfg: dict[str, Any]) -> tuple[Path, str, int, int, str, str]:
    chroma_cfg = vcfg.get("chroma", {})
    persist_dir_str = chroma_cfg["persist_dir"]
    persist_dir = expand_path(persist_dir_str)
    collection_name = str(chroma_cfg["collection_name"])
    embed_model = vcfg.get("embedding_model") or ""
    llm_model = vcfg.get("llm_model") or ""
    if not embed_model or not llm_model:
        raise RuntimeError("embedding_model and llm_model must be set in vector_db config.")
    top_k = int(vcfg["top_k"])
    max_prompt_chars = int(vcfg["max_prompt_chars"])
    return persist_dir, collection_name, top_k, max_prompt_chars, embed_model, llm_model


def _verify_index(persist_dir: Path, collection_name: str) -> int:
    client = chromadb.PersistentClient(path=str(persist_dir))
    collection = client.get_or_create_collection(collection_name)
    return collection.count()


def _test_rag(
    question: str,
    persist_dir: Path,
    collection_name: str,
    top_k: int,
    max_prompt_chars: int,
    embed_model: str,
    llm_model: str,
    system_prompt: str,
) -> str:
    client = chromadb.PersistentClient(path=str(persist_dir))
    collection = client.get_or_create_collection(collection_name)
    q_emb = embed_query(question, model=embed_model)
    results = collection.query(query_embeddings=[q_emb], n_results=top_k)
    docs = results.get("documents") or [[]]
    contexts = docs[0] if docs else []
    prompt = build_prompt(question, contexts, system_prompt, max_prompt_chars)
    resp = ollama.chat(model=llm_model, messages=[{"role": "user", "content": prompt}])
    return resp.message.content


def initialise() -> None:
    doc_cfg = load_doc_config()
    vcfg = load_vector_config()
    ocfg = load_ollama_config()

    _validate_rag_config(doc_cfg, vcfg)
    pdf_path = _ensure_pdf_exists(doc_cfg)
    _ensure_ollama_server()
    _ensure_models_installed(ocfg)

    persist_dir, collection_name, top_k, max_prompt_chars, embed_model, llm_model = _vector_store_params(vcfg)
    persist_dir.mkdir(parents=True, exist_ok=True)

    build_index()

    count = _verify_index(persist_dir, collection_name)
    if count == 0:
        raise RuntimeError("Chroma index is empty after ingestion.")

    question = str(ocfg["test_question"])
    system_prompt = str(ocfg["system_prompt"])
    answer = _test_rag(
        question=question,
        persist_dir=persist_dir,
        collection_name=collection_name,
        top_k=top_k,
        max_prompt_chars=max_prompt_chars,
        embed_model=embed_model,
        llm_model=llm_model,
        system_prompt=system_prompt,
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
