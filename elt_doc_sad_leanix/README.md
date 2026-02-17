# elt_doc_sad_leanix

Generate LeanIX diagrams.net XML files from Workday SAD (.docx) documents.

## Quick Start

### Use the skill via Claude Code

```bash
cd /Users/rpatel/Documents/__code/git/emailrak/elt_lake
claude
```

Then prompt:

```
Generate LeanIX diagram.net xml file for the workday integration from the SAD document: ~/Downloads/phase0_workday_sad/SAD_INT004_AMEX_GBT_V1_0.docx
```

Claude will automatically:
1. Read the SKILL.md and recognise the request
2. Parse the SAD `.docx` using `python-docx` (via `uv run --package elt-doc-sad-leanix python ...`)
3. Extract integration ID, vendor name, direction, security details
4. Select the appropriate template (outbound EIB, bi-directional API, multi-connector, or via FA SFTP)
5. Generate a diagrams.net XML file saved alongside the input SAD document

The output XML can be imported directly into LeanIX.

**For overview/consolidation diagrams**, see the separate `elt_doc_leanix_overview` package and `leanix-overview` skill.

## How It Works

This project is a **uv workspace member**. The workspace root is `elt_lake/`, and this module (`elt_doc_sad_leanix`) is one of its members.

The Claude Code skill (`.claude/skills/leanix-from-sad/SKILL.md`) tells Claude to run Python with:

```bash
uv run --package elt-doc-sad-leanix python <script.py>
```

The `--package` flag ensures this member's dependencies (`python-docx`, `openpyxl`) are installed in the shared workspace `.venv` before execution.

## Project Structure

```
elt_doc_sad_leanix/
├── pyproject.toml                              # python-docx, openpyxl deps (shared)
├── README.md
├── inspect_excel.py                            # Utility: inspect LeanIX inventory Excel
├── src/elt_doc_sad_leanix/
│   ├── __init__.py
│   ├── py.typed
│   ├── diagram_generator.py                    # WorkdayIntegrationDiagramGenerator [Step3][Skill]
│   ├── cmd/
│   │   ├── sad_pipeline.py                     # Trae helper [Step1][Step3]
│   │   ├── build_xml.py                        # JSON spec → XML (CLI) [Step3][Skill]
│   │   └── compile_context.py                  # Build LLM prompt [Step1][Skill]
│   ├── prompts/
│   │   └── sad_to_leanix.md                    # LLM prompt template [Step1/2][Skill]
│   └── legacy/
│       └── generate_from_sad.py                # Legacy SAD → XML (not in 3-step)
├── config/
│   └── LeanIX_Inventory.xlsx                   # LeanIX asset inventory [Step1][Step3][Skill]
├── templates/                                  # XML baselines [Step1][Step3][Skill]
│   ├── integration_bidirectional_api.xml        # Workday ↔ Vendor
│   ├── integration_outbound_fa_sftp.xml         # Workday → FA SFTP → Vendor
│   ├── integration_outbound_vendor_sftp.xml     # Workday → Vendor SFTP → Vendor
│   ├── integration_inbound_fa_sftp.xml          # Vendor → FA SFTP → Workday
│   └── integration_multi_connector.xml          # Workday ↔ Gateway ↔ Vendor
└── test/
```

## Trae / CLI Workflow

For Trae (or any CLI that cannot call the LLM directly), use the `sad_pipeline.py` helper. It wraps the prompt compilation and XML build; Trae handles only the JSON step.

1. **Generate the prompt from a SAD document**

   ```bash
   cd /Users/rpatel/Documents/__code/git/emailrak/elt_lake

   uv run --package elt-doc-sad-leanix python \
     elt_doc_sad_leanix/src/elt_doc_sad_leanix/cmd/sad_pipeline.py \
     ~/Downloads/phase0_workday_sad/SAD_INT003_Headspace_V1_0.docx \
     --output-dir .tmp
   ```

   This writes a prompt file like:

   ```text
   .tmp/prompts/SAD_INT003_Headspace_V1_0_prompt.md
   ```

   The script also prints a single line you can copy/paste into Trae, for example:

   ```text
   Process the prompt in `/Users/rpatel/Documents/__code/git/emailrak/elt_lake/.tmp/prompts/SAD_INT003_Headspace_V1_0_prompt.md`, generate the JSON spec exactly as described in the schema in that prompt, and save it to `/Users/rpatel/Documents/__code/git/emailrak/elt_lake/.tmp/specs/SAD_INT003_Headspace_V1_0_spec.json`.
   ```

2. **Paste that line into Trae**

3. **Build the diagrams.net XML from the JSON spec**

   ```bash
   uv run --package elt-doc-sad-leanix python \
     elt_doc_sad_leanix/src/elt_doc_sad_leanix/cmd/sad_pipeline.py \
     ~/Downloads/phase0_workday_sad/SAD_INT003_Headspace_V1_0.docx \
     --output-dir .tmp \
     --json-spec SAD_INT003_Headspace_V1_0_spec.json
   ```

   This produces a LeanIX‑importable XML file in `.tmp/xml/`.

The helper:

- Uses the same prompt template and inventory as `compile_context.py`.
- Uses `diagram_generator.py` under the hood to produce LeanIX‑compatible diagrams.net XML.

### Summary

- Step 1 (Python): Build a prompt for the LLM that includes the SAD text extract, LeanIX inventory table, and available XML templates. Output → `.tmp/prompts/<SAD>_prompt.md`, plus a one‑line instruction telling the LLM to save JSON to `.tmp/specs/<SAD>_spec.json`.
- Step 2 (LLM): Read that prompt and generate the JSON spec (`template_id`, process sections, IDs where possible). Output → `.tmp/specs/<SAD>_spec.json`.
- Step 3 (Python): Read the JSON and build the diagrams.net XML. If `template_id` exists, use the file under `templates/` and substitute IDs, labels, and table content. Output → `.tmp/xml/<SPEC>.xml`.

You can use any model for Step 2 (Trae, Qwen, local Ollama) as long as it:
- Can read the `.tmp/prompts/<SAD>_prompt.md` file content
- Writes strict JSON to the path printed in the Step 1 instruction

### File Dependencies (concise)

- Prompt template: `elt_doc_sad_leanix/src/elt_doc_sad_leanix/prompts/sad_to_leanix.md`
- Templates (XML baselines): `elt_doc_sad_leanix/templates/*.xml`
- LeanIX inventory (asset IDs): `elt_doc_sad_leanix/config/LeanIX_Inventory.xlsx`
- SAD source: your `.docx` (read via `python-docx`)
- Python libs: `python-docx`, `openpyxl`

### Orchestrated Skill Option

As an alternative to running the three steps manually, you can let Trae orchestrate the whole workflow via the `leanix-from-sad-orchestrated` skill in `.trae/skills/`.

Example chat invocation (with Qwen or a local Ollama model active in Trae):

> Using a local model only, generate the LeanIX diagrams.net XML for `~/Downloads/phase0_workday_sad/SAD_INT003_Headspace_V1_0.docx` using the orchestrated SAD workflow.

The skill will:
- Run Step 1 (Python) to build the prompt and JSON instruction
- Call the active model to perform Step 2 and write the JSON spec
- Run Step 3 (Python) to produce `.tmp/xml/<SPEC>.xml` for LeanIX import
