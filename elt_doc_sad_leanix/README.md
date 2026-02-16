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
Generate LeanIX diagram.net xml file for the workday integration from the SAD document: ~/Downloads/SAD_INT018_Barclays_Banking_v1_0.docx
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
├── pyproject.toml                              # python-docx, openpyxl dependencies
├── README.md
├── inspect_excel.py                            # Utility: inspect LeanIX inventory Excel
├── src/elt_doc_sad_leanix/
│   ├── __init__.py
│   ├── py.typed
│   ├── diagram_generator.py                    # WorkdayIntegrationDiagramGenerator class
│   ├── cmd/
│   │   ├── build_xml.py                        # JSON spec → XML builder (CLI)
│   │   └── compile_context.py                  # Assembles LLM prompt from inventory + SAD
│   ├── prompts/
│   │   └── sad_to_leanix.md                    # LLM prompt template for JSON generation
│   └── legacy/
│       └── generate_from_sad.py                # Legacy: direct SAD parsing → XML
├── config/
│   └── LeanIX_Inventory.xlsx                   # LeanIX asset inventory
├── templates/
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
   .tmp/SAD_INT003_Headspace_V1_0_prompt.md
   ```

   The script also prints a single line you can copy/paste into Trae, for example:

   ```text
   Process the prompt in `/Users/rpatel/Documents/__code/git/emailrak/elt_lake/.tmp/SAD_INT003_Headspace_V1_0_prompt.md`, generate the JSON spec exactly as described in the schema in that prompt, and save it to `/Users/rpatel/Documents/__code/git/emailrak/elt_lake/.tmp/SAD_INT003_Headspace_V1_0_spec.json`.
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

   This produces a LeanIX‑importable XML file in `.tmp/`.

The helper:

- Uses the same prompt template and inventory as `compile_context.py`.
- Uses `diagram_generator.py` under the hood to produce LeanIX‑compatible diagrams.net XML.
