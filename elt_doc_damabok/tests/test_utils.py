from elt_doc_damabok import utils


def test_load_configs_have_expected_keys() -> None:
    doc_cfg = utils.load_doc_config()
    assert "source_pdf" in doc_cfg
    assert "chunk_size" in doc_cfg
    assert "chunk_overlap" in doc_cfg

    vcfg = utils.load_vector_config()
    assert "embedding_model" in vcfg
    assert "llm_model" in vcfg
    assert "top_k" in vcfg
    assert "max_prompt_chars" in vcfg

    ocfg = utils.load_ollama_config()
    assert "models" in ocfg
    assert "system_prompt" in ocfg
    assert "test_question" in ocfg


def test_build_prompt_respects_max_chars() -> None:
    contexts = ["x" * 1000 for _ in range(20)]
    prompt = utils.build_prompt(
        question="Q",
        contexts=contexts,
        system_prompt="S",
        max_prompt_chars=3000,
    )
    assert len(prompt) <= 3000
