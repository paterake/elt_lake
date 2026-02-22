from __future__ import annotations

import chromadb

import ollama
from elt_doc_damabok.utils import (
    build_prompt,
    embed_query,
    expand_path,
    load_ollama_config,
    load_vector_config,
)


def interactive_qa() -> None:
    vcfg = load_vector_config()
    ocfg = load_ollama_config()
    system_prompt = str(ocfg["system_prompt"])
    embed_model = str(vcfg["embedding_model"])
    llm_model = str(vcfg["llm_model"])
    chroma_cfg = vcfg.get("chroma", {})
    persist_dir = expand_path(chroma_cfg["persist_dir"])
    collection_name = str(chroma_cfg["collection_name"])
    top_k = int(vcfg["top_k"])

    client = chromadb.PersistentClient(path=str(persist_dir))
    collection = client.get_or_create_collection(collection_name)

    while True:
        try:
            q = input("DMBOK question (or 'quit'): ").strip()
        except EOFError:
            break
        if not q or q.lower() in {"quit", "exit"}:
            break

        q_emb = embed_query(q, model=embed_model)
        results = collection.query(query_embeddings=[q_emb], n_results=top_k)
        docs = results.get("documents") or [[]]
        contexts = docs[0] if docs else []

        prompt = build_prompt(q, contexts, system_prompt, int(vcfg["max_prompt_chars"]))
        resp = ollama.chat(model=llm_model, messages=[{"role": "user", "content": prompt}])
        print("\n--- Answer ---\n")
        print(resp.message.content)
        print("\n-------------\n")


def main() -> None:
    interactive_qa()


if __name__ == "__main__":
    main()
