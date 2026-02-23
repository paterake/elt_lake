"""Initialisation and validation for DMBOK RAG system."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import chromadb
import ollama

from elt_doc_damabok.constants import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_LLM_MODEL,
    DEFAULT_TOP_K,
    MAX_CHUNK_OVERLAP,
    MAX_CHUNK_SIZE,
    MAX_TOP_K,
    MIN_CHUNK_OVERLAP,
    MIN_CHUNK_SIZE,
    MIN_TOP_K,
    SUPPORTED_CHUNKING_STRATEGIES,
)
from elt_doc_damabok.ingest import build_index
from elt_doc_damabok.utils import (
    build_prompt,
    embed_query,
    expand_path,
    load_doc_config,
    load_ollama_config,
    load_vector_config,
)

logger = logging.getLogger(__name__)


class RagConfigError(Exception):
    """Exception raised for RAG configuration errors."""
    pass


class OllamaError(Exception):
    """Exception raised for Ollama-related errors."""
    pass


def _validate_rag_config(doc_cfg: dict[str, Any], vcfg: dict[str, Any]) -> None:
    """Validate RAG configuration parameters.
    
    Args:
        doc_cfg: Document configuration.
        vcfg: Vector database configuration.
        
    Raises:
        RagConfigError: If configuration is invalid.
    """
    logger.debug("Validating RAG configuration")
    
    chunk_size = int(doc_cfg.get("chunk_size", DEFAULT_CHUNK_SIZE))
    chunk_overlap = int(doc_cfg.get("chunk_overlap", DEFAULT_CHUNK_OVERLAP))
    chunking_strategy = str(doc_cfg.get("chunking_strategy", "page"))
    top_k = int(vcfg.get("top_k", DEFAULT_TOP_K))
    max_prompt_chars = int(vcfg["max_prompt_chars"])
    
    # Validate chunking strategy
    if chunking_strategy not in SUPPORTED_CHUNKING_STRATEGIES:
        raise RagConfigError(
            f"Unsupported chunking_strategy '{chunking_strategy}'. "
            f"Supported: {sorted(SUPPORTED_CHUNKING_STRATEGIES)}"
        )
    
    # Validate chunk size
    if not (MIN_CHUNK_SIZE <= chunk_size <= MAX_CHUNK_SIZE):
        raise RagConfigError(
            f"chunk_size ({chunk_size}) must be between "
            f"{MIN_CHUNK_SIZE} and {MAX_CHUNK_SIZE}"
        )
    
    # Validate chunk overlap
    if not (MIN_CHUNK_OVERLAP <= chunk_overlap <= MAX_CHUNK_OVERLAP):
        raise RagConfigError(
            f"chunk_overlap ({chunk_overlap}) must be between "
            f"{MIN_CHUNK_OVERLAP} and {MAX_CHUNK_OVERLAP}"
        )
    
    # Validate overlap < size
    if chunk_overlap >= chunk_size:
        raise RagConfigError(
            f"chunk_overlap ({chunk_overlap}) must be less than "
            f"chunk_size ({chunk_size})"
        )
    
    # Validate top_k
    if not (MIN_TOP_K <= top_k <= MAX_TOP_K):
        raise RagConfigError(
            f"top_k ({top_k}) must be between {MIN_TOP_K} and {MAX_TOP_K}"
        )
    
    # Validate prompt size
    if top_k * chunk_size > max_prompt_chars:
        raise RagConfigError(
            f"top_k ({top_k}) × chunk_size ({chunk_size}) = {top_k * chunk_size} chars "
            f"exceeds max_prompt_chars ({max_prompt_chars}). "
            f"Reduce top_k or chunk_size, or increase max_prompt_chars."
        )
    
    logger.info(
        "RAG configuration valid: chunk_size=%d, overlap=%d, top_k=%d",
        chunk_size,
        chunk_overlap,
        top_k,
    )


def _ensure_pdf_exists(doc_cfg: dict[str, Any]) -> Path:
    """Verify PDF file exists.
    
    Args:
        doc_cfg: Document configuration.
        
    Returns:
        Resolved PDF path.
        
    Raises:
        FileNotFoundError: If PDF not found.
    """
    pdf_path = expand_path(doc_cfg["source_pdf"])
    
    if not pdf_path.is_file():
        logger.error("DMBOK PDF not found at: %s", pdf_path)
        raise FileNotFoundError(f"DMBOK PDF not found at {pdf_path}")
    
    logger.info("DMBOK PDF found at: %s", pdf_path)
    return pdf_path


def _ensure_ollama_server() -> None:
    """Verify Ollama server is available.
    
    Raises:
        OllamaError: If Ollama server not reachable.
    """
    logger.debug("Checking Ollama server")
    
    try:
        ollama.list()
        logger.info("Ollama server is available")
    except Exception as exc:
        logger.error("Unable to reach Ollama server")
        raise OllamaError(
            "Unable to reach Ollama server. Ensure 'ollama serve' is running."
        ) from exc


def _ensure_models_installed(ocfg: dict[str, Any]) -> None:
    """Verify required models are installed.
    
    Args:
        ocfg: Ollama configuration.
        
    Raises:
        OllamaError: If models not available.
    """
    logger.debug("Checking required models")
    
    models_cfg = ocfg.get("models") or []
    
    if not isinstance(models_cfg, list) or not models_cfg:
        raise OllamaError("No models defined in ollama config.")
    
    names: set[str] = {str(m) for m in models_cfg}
    logger.info("Required models: %s", names)
    
    # Check installed models
    listed = ollama.list()
    installed = {m.model.removesuffix(":latest") for m in listed.models}
    logger.debug("Installed models: %s", installed)
    
    # Pull missing models
    for model in names:
        model_base = model.removesuffix(":latest")
        if model_base not in installed:
            logger.info("Pulling missing model: %s", model)
            try:
                for _ in ollama.pull(model=model):
                    pass
                logger.debug("Model pulled: %s", model)
            except Exception as e:
                logger.error("Failed to pull model %s: %s", model, e)
                raise OllamaError(f"Failed to pull model {model}: {e}")
    
    # Verify all models now available
    listed_after = ollama.list()
    installed_after = {m.model.removesuffix(":latest") for m in listed_after.models}
    missing = [m for m in names if m.removesuffix(":latest") not in installed_after]
    
    if missing:
        logger.error("Models still missing after pull: %s", missing)
        raise OllamaError(f"Models not available after pull: {missing}")
    
    logger.info("All required models are installed")


def _vector_store_params(vcfg: dict[str, Any]) -> tuple[Path, str, int, int, str, str]:
    """Extract vector store parameters from config.
    
    Args:
        vcfg: Vector database configuration.
        
    Returns:
        Tuple of (persist_dir, collection_name, top_k, max_prompt_chars, embed_model, llm_model).
        
    Raises:
        RagConfigError: If required parameters missing.
    """
    chroma_cfg = vcfg.get("chroma", {})
    persist_dir_str = chroma_cfg.get("persist_dir", "./damabok_chroma")
    persist_dir = expand_path(persist_dir_str)
    collection_name = str(chroma_cfg.get("collection_name", "damabok"))
    
    embed_model = vcfg.get("embedding_model")
    llm_model = vcfg.get("llm_model")
    
    if not embed_model or not llm_model:
        raise RagConfigError(
            "embedding_model and llm_model must be set in vector_db config."
        )
    
    top_k = int(vcfg.get("top_k", DEFAULT_TOP_K))
    max_prompt_chars = int(vcfg["max_prompt_chars"])
    
    logger.debug(
        "Vector store params: persist_dir=%s, collection=%s, top_k=%d",
        persist_dir,
        collection_name,
        top_k,
    )
    
    return persist_dir, collection_name, top_k, max_prompt_chars, embed_model, llm_model


def _verify_index(persist_dir: Path, collection_name: str) -> int:
    """Verify Chroma index has documents.
    
    Args:
        persist_dir: Chroma persistence directory.
        collection_name: Collection name.
        
    Returns:
        Document count.
    """
    logger.debug("Verifying index: %s", collection_name)
    
    client = chromadb.PersistentClient(path=str(persist_dir))
    collection = client.get_or_create_collection(collection_name)
    count = collection.count()
    
    logger.info("Index contains %d documents", count)
    return count


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
    """Test RAG system with a question.
    
    Args:
        question: Test question.
        persist_dir: Chroma persistence directory.
        collection_name: Collection name.
        top_k: Number of contexts to retrieve.
        max_prompt_chars: Maximum prompt length.
        embed_model: Embedding model name.
        llm_model: LLM model name.
        system_prompt: System prompt.
        
    Returns:
        LLM answer.
        
    Raises:
        RuntimeError: If RAG test fails.
    """
    logger.info("Testing RAG with question: %s", question[:100])
    
    client = chromadb.PersistentClient(path=str(persist_dir))
    collection = client.get_or_create_collection(collection_name)
    
    # Embed query
    q_emb = embed_query(question, model=embed_model)
    
    # Retrieve
    results = collection.query(query_embeddings=[q_emb], n_results=top_k)
    docs = results.get("documents") or [[]]
    contexts = docs[0] if docs else []
    
    logger.debug("Retrieved %d contexts", len(contexts))
    
    if not contexts:
        raise RuntimeError("No contexts retrieved for test question")
    
    # Build prompt
    prompt = build_prompt(question, contexts, system_prompt, max_prompt_chars)
    
    # Call LLM
    logger.debug("Calling LLM: %s", llm_model)
    resp = ollama.chat(model=llm_model, messages=[{"role": "user", "content": prompt}])
    
    answer = resp.message.content
    logger.info("RAG test successful: %d character answer", len(answer))
    
    return answer


def initialise() -> None:
    """Initialise and validate the DMBOK RAG system.
    
    This function:
    1. Validates configuration
    2. Checks PDF exists
    3. Checks Ollama server
    4. Checks models installed
    5. Builds index
    6. Verifies index
    7. Runs test question
    
    Raises:
        RagConfigError: If configuration invalid.
        OllamaError: If Ollama issues.
        FileNotFoundError: If PDF not found.
        RuntimeError: If initialisation fails.
    """
    logger.info("Starting DMBOK RAG initialisation")
    
    # Load configuration
    logger.debug("Loading configuration")
    doc_cfg = load_doc_config()
    vcfg = load_vector_config()
    ocfg = load_ollama_config()
    
    # Validate configuration
    _validate_rag_config(doc_cfg, vcfg)
    
    # Check PDF
    pdf_path = _ensure_pdf_exists(doc_cfg)
    
    # Check Ollama
    _ensure_ollama_server()
    
    # Check models
    _ensure_models_installed(ocfg)
    
    # Extract parameters
    persist_dir, collection_name, top_k, max_prompt_chars, embed_model, llm_model = (
        _vector_store_params(vcfg)
    )
    
    # Ensure persist directory exists
    persist_dir.mkdir(parents=True, exist_ok=True)
    
    # Build index
    logger.info("Building index")
    build_index()
    
    # Verify index
    count = _verify_index(persist_dir, collection_name)
    if count == 0:
        raise RuntimeError("Chroma index is empty after ingestion")
    
    # Test RAG
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
    
    # Print summary
    print("\n" + "=" * 60)
    print("DMBOK RAG Initialisation Complete")
    print("=" * 60)
    print(f"PDF: {pdf_path}")
    print(f"Chroma: {persist_dir} ({collection_name})")
    print(f"Documents: {count}")
    print(f"Test Question: {question}")
    print(f"Answer: {answer[:200]}...")
    print("=" * 60)
    
    logger.info("Initialisation complete")


def main() -> None:
    """CLI entry point for initialisation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialise DMBOK RAG system")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    try:
        initialise()
    except RagConfigError as e:
        print(f"Configuration error: {e}")
        raise SystemExit(1)
    except OllamaError as e:
        print(f"Ollama error: {e}")
        raise SystemExit(1)
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        raise SystemExit(1)
    except RuntimeError as e:
        print(f"Error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
