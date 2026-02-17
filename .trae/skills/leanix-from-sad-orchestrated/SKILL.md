---
name: "leanix-from-sad-orchestrated"
description: "End-to-end SAD→LeanIX XML. Invoke when user asks to fully automate integration diagram generation from a Workday SAD using any (including local) model."
---

# LeanIX from SAD (Orchestrated, Model-Agnostic)

## Purpose

Run the full 3-step SAD→LeanIX diagrams.net XML workflow automatically using whatever model is active in Trae (Qwen, local Ollama, etc.). Use this when the user asks to *generate a LeanIX/diagrams.net XML for a Workday integration SAD* and wants it done end-to-end without manually copying prompts.

This skill:
- Calls Python to build the prompt and context from the SAD and inventory
- Uses the active LLM to generate the JSON spec
- Calls Python again to generate the diagrams.net XML
- Leaves the final XML ready to import into LeanIX

## When to Use

- User says: “Generate the LeanIX / diagrams.net XML from this SAD”
- User references an integration ID (e.g. INT003, INT006, INT018) and a SAD `.docx`
- User wants to avoid manual copy/paste of prompts or JSON
- Works with any model Trae is currently using (Qwen, Claude, local Ollama, etc.)
- Especially use this when the user says they are using a **local** model only (e.g. Ollama) and still wants the full SAD→LeanIX flow automated.

Do **not** use this for overview/consolidation diagrams — use the overview skill/package instead.

## Requirements

- Workspace: this repo checked out at:
  - `/Users/rpatel/Documents/__code/git/emailrak/elt_lake`
- Python project: `elt_doc_sad_leanix` with dependencies installed via `uv`
- SAD document path provided by the user (e.g. `~/Downloads/phase0_workday_sad/SAD_INT003_Headspace_V1_0.docx`)

## Example Chat Invocations

Use these as triggers in Trae:

- “Using my local Ollama model, generate the LeanIX diagrams.net XML for `~/Downloads/phase0_workday_sad/SAD_INT003_Headspace_V1_0.docx` using the orchestrated SAD workflow.”
- “Run the full SAD to LeanIX pipeline (prompt → JSON → XML) for `~/Downloads/phase0_workday_sad/SAD_INT006_Barclaycard_Visa_Credit_Card_v1_0.docx`.”
- “From this Workday SAD, produce a LeanIX-importable diagrams.net XML using the orchestrated skill (no cloud calls, only local model).”

## Orchestrated Workflow

### 1. Build the prompt and instruction (Python)

1. From the workspace root, run:

   ```bash
   cd /Users/rpatel/Documents/__code/git/emailrak/elt_lake

   uv run --package elt-doc-sad-leanix python \
     elt_doc_sad_leanix/src/elt_doc_sad_leanix/cmd/sad_pipeline.py \
     <SAD_PATH> \
     --output-dir .tmp
   ```

   - Example:

     ```bash
     uv run --package elt-doc-sad-leanix python \
       elt_doc_sad_leanix/src/elt_doc_sad_leanix/cmd/sad_pipeline.py \
       ~/Downloads/phase0_workday_sad/SAD_INT003_Headspace_V1_0.docx \
       --output-dir .tmp
     ```

2. Capture from stdout:
   - The generated prompt path (under `.tmp/prompts/…_prompt.md`)
   - The one-line instruction that tells the LLM to save JSON to `.tmp/specs/…_spec.json`

### 2. Use the active model to generate the JSON spec

3. Read the generated prompt file content from `.tmp/prompts/<SAD>_prompt.md`.

4. Run an in-memory LLM call (using the currently active model in Trae) with that prompt and follow the schema instructions exactly. The goal is to produce the JSON spec:
   - `template_id`
   - `title`
   - `integration_id`
   - `direction`
   - `source_system`, `target_system`, optional `intermediary`
   - Process sections, labels, and any IDs the model can confidently infer

5. Save the JSON output to the exact path indicated in the step 1 instruction:
   - `.tmp/specs/<SAD>_spec.json`

**Important:** Do **not** change the output path; use the exact file path mentioned in the instruction so that the next step can find it.

### 3. Build the diagrams.net XML (Python)

6. From the workspace root, run:

   ```bash
   cd /Users/rpatel/Documents/__code/git/emailrak/elt_lake

   uv run --package elt-doc-sad-leanix python \
     elt_doc_sad_leanix/src/elt_doc_sad_leanix/cmd/sad_pipeline.py \
     <SAD_PATH> \
     --output-dir .tmp \
     --json-spec <SPEC_FILENAME>.json
   ```

   - Example:

     ```bash
     uv run --package elt-doc-sad-leanix python \
       elt_doc_sad_leanix/src/elt_doc_sad_leanix/cmd/sad_pipeline.py \
       ~/Downloads/phase0_workday_sad/SAD_INT003_Headspace_V1_0.docx \
       --output-dir .tmp \
       --json-spec SAD_INT003_Headspace_V1_0_spec.json
     ```

7. This will:
   - Load the JSON spec from `.tmp/specs/…`
   - Resolve missing LeanIX IDs from `config/LeanIX_Inventory.xlsx`
   - Use the appropriate template under `elt_doc_sad_leanix/templates/` when `template_id` is set
   - Write the final diagrams.net XML to `.tmp/xml/<SPEC>_.xml`

### 4. Hand-off to the User

8. After step 3 completes, surface to the user:
   - The full path of the generated XML file under `.tmp/xml/…`
   - A brief note that it can be imported into LeanIX as a standard diagrams.net XML

## Model-Agnostic Notes

- This skill does not assume a specific model provider. Whatever model Trae is currently using (Qwen, Claude, local Ollama) should:
  - Obey the prompt schema in `sad_to_leanix.md`
  - Produce strict JSON (no extra commentary)
- If the JSON parse fails, re-run the model with instructions to output only valid JSON.

### Local / Offline Model Guidance

- When the user states that only local models are allowed (e.g. for confidential company data), ensure Trae is configured to use a local provider (such as Ollama) and do not rely on any cloud tools or web search.
- All SAD content and LeanIX inventory data must remain on the local filesystem; do not send these documents to external APIs.
- Prefer models that:
  - Handle long prompts reliably (SAD text + inventory + templates)
  - Are good at producing well-formed JSON on request
- If the local model struggles with JSON formatting, use short, explicit instructions like: “Output only valid JSON matching the schema. No explanations or extra text.”

### Recommended Ollama Models and Settings

When Trae is configured to talk to a local Ollama server (default: `http://localhost:11434`), use one of these models for the JSON-spec step:

- `qwen2.5-coder:14b` (preferred)
  - Best balance of reasoning, long-context handling, and JSON reliability for SAD→spec.
- `qwen2.5-coder:7b`
  - Lighter-weight option if resources are limited; still good for structured JSON.
- `deepseek-coder:6.7b-instruct-q4_K_M`
  - Strong for code-heavy reasoning; may require stricter JSON instructions.
- `llama3.1:8b`
  - Good general model; use only if the coder models are unavailable.

Suggested defaults when calling Ollama from Trae/tools:

- Temperature: 0.1–0.3
- Top_p: 0.9
- Sufficient context window to include:
  - Full prompt from `sad_to_leanix.md`
  - Inventory extract
  - SAD text extract

Always prepend a short system-style instruction before the prompt content when using Ollama, for example:

> You are generating a JSON spec for a LeanIX integration diagram. Follow the schema exactly and output only valid JSON, no explanations.
