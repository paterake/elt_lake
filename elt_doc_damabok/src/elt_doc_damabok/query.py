"""Query pipeline for DMBOK RAG system."""

from __future__ import annotations

import logging

import chromadb

import ollama
from elt_doc_damabok.constants import (
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_LLM_MODEL,
    DEFAULT_TOP_K,
)
from elt_doc_damabok.utils import (
    build_prompt,
    embed_query,
    expand_path,
    load_ollama_config,
    load_vector_config,
)

logger = logging.getLogger(__name__)


def interactive_qa() -> None:
    """Run interactive Q&A session against DMBOK index."""
    logger.info("Starting interactive Q&A session")
    
    # Load configuration
    logger.debug("Loading configuration")
    vcfg = load_vector_config()
    ocfg = load_ollama_config()
    
    system_prompt = str(ocfg["system_prompt"])
    embed_model = str(vcfg.get("embedding_model", DEFAULT_EMBEDDING_MODEL))
    llm_model = str(vcfg.get("llm_model", DEFAULT_LLM_MODEL))
    
    chroma_cfg = vcfg.get("chroma", {})
    persist_dir = expand_path(chroma_cfg["persist_dir"])
    collection_name = str(chroma_cfg["collection_name"])
    top_k = int(vcfg.get("top_k", DEFAULT_TOP_K))
    max_prompt_chars = int(vcfg["max_prompt_chars"])
    
    logger.info(
        "Configuration: model=%s, embed=%s, top_k=%d, persist_dir=%s",
        llm_model,
        embed_model,
        top_k,
        persist_dir,
    )
    
    # Initialize Chroma
    logger.debug("Connecting to Chroma: %s", persist_dir)
    client = chromadb.PersistentClient(path=str(persist_dir))
    collection = client.get_or_create_collection(collection_name)
    
    print("DMBOK Q&A Session (type 'quit' to exit)")
    logger.info("Q&A session ready")
    
    while True:
        try:
            q = input("\nQuestion: ").strip()
        except EOFError:
            logger.info("EOF received, exiting")
            break
        except KeyboardInterrupt:
            logger.info("Interrupt received, exiting")
            print()
            break
        
        if not q:
            continue
        
        if q.lower() in {"quit", "exit", "q"}:
            logger.info("User quit, exiting")
            print("Goodbye!")
            break
        
        logger.info("Processing question: %s", q[:100])
        
        try:
            # Embed query
            logger.debug("Embedding query")
            q_emb = embed_query(q, model=embed_model)
            
            # Retrieve contexts
            logger.debug("Retrieving top %d contexts", top_k)
            results = collection.query(query_embeddings=[q_emb], n_results=top_k)
            docs = results.get("documents") or [[]]
            contexts = docs[0] if docs else []
            
            logger.debug("Retrieved %d contexts", len(contexts))
            
            if not contexts:
                print("\nNo relevant documents found.")
                continue
            
            # Build prompt
            prompt = build_prompt(q, contexts, system_prompt, max_prompt_chars)
            
            # Call LLM
            logger.debug("Calling LLM: %s", llm_model)
            resp = ollama.chat(
                model=llm_model,
                messages=[{"role": "user", "content": prompt}],
            )
            
            answer = resp.message.content
            
            print("\n--- Answer ---\n")
            print(answer)
            print("\n---------------\n")
            
            logger.info("Answer generated: %d characters", len(answer))
            
        except Exception as e:
            logger.exception("Error processing question")
            print(f"\nError: {e}\n")


def main() -> None:
    """CLI entry point for query."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Query DMBOK RAG index")
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
    
    interactive_qa()


if __name__ == "__main__":
    main()
