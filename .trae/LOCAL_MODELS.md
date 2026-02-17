# Trae Local Models (Ollama / Qwen) and SAD→LeanIX

This repo is designed to work with **local models** (e.g. Ollama) as well as cloud models. This page explains how to use them with the SAD→LeanIX workflow.

## 1. Using Local Ollama Models in Trae

Prerequisites:

- Ollama installed and running locally:
  - `ollama serve` (or launch via your OS)
- Models pulled, for example:
  - `qwen2.5-coder:14b`
  - `qwen2.5-coder:7b`
  - `deepseek-coder:6.7b-instruct-q4_K_M`
  - `llama3.1:8b`

Configure Trae:

- Set the model provider to use a local endpoint (such as an Ollama server at `http://localhost:11434`).
- Choose one of the local models above as the default. For SAD→LeanIX JSON generation:
  - Prefer `qwen2.5-coder:14b`
  - Or `qwen2.5-coder:7b` if you want something lighter

Once Trae is pointing at Ollama, any skill or workflow that calls the model (including the SAD→LeanIX orchestration) will run entirely on your machine. No SAD content or inventory data needs to leave the local environment.

## 2. Orchestrated SAD→LeanIX Workflow (Single-Step)

The `.trae/skills/leanix-from-sad-orchestrated/SKILL.md` skill automates the 3-step pipeline:

1. Calls Python to run `sad_pipeline.py` (Step 1) and build `.tmp/prompts/<SAD>_prompt.md` and the JSON instruction
2. Uses the active model (local Ollama, Qwen, etc.) to generate the JSON spec into `.tmp/specs/<SAD>_spec.json`
3. Calls `sad_pipeline.py` again (Step 3) to produce `.tmp/xml/<SPEC>.xml` for LeanIX import

Example Trae prompt (with a local model active):

> Using my local model only, generate the LeanIX diagrams.net XML for `~/Downloads/phase0_workday_sad/SAD_INT003_Headspace_V1_0.docx` using the orchestrated SAD workflow.

## 3. Using Local or Remote Models for Step 2

You can use local Ollama models, Qwen, or other providers for Step 2 in both workflows.

### Manual 3-Step Workflow (README Steps 1–3)

- Step 1: Run `sad_pipeline.py` to generate `.tmp/prompts/<SAD>_prompt.md` and print the JSON-save instruction.
- Step 2: In Trae (or any LLM client), with your chosen model:
  - Open the prompt file `.tmp/prompts/<SAD>_prompt.md`.
  - Ask the model to follow the schema and write the JSON spec to the exact path printed (e.g. `.tmp/specs/<SAD>_spec.json`).
- Step 3: Run `sad_pipeline.py` again with `--json-spec` to build the XML.

### Orchestrated Workflow

- The `leanix-from-sad-orchestrated` skill performs Step 2 internally using whichever model Trae is currently configured to use.
- To switch between Qwen and local Ollama:
  - Adjust Trae’s model provider settings (no changes to this repo are needed).

### JSON Quality Tips

- For local models, keep temperature low (around 0.1–0.3) for Step 2.
- Add a short system-style instruction before the prompt content, for example:

> You are generating a JSON spec for a LeanIX integration diagram. Follow the schema exactly and output only valid JSON, no explanations.

