# elt_doc_sad_leanix

Generate LeanIX diagrams.net XML files from Workday SAD (.docx) documents.

## Quick Start

### Step 1: Use the skill via Claude Code

```bash
cd /Users/rpatel/Documents/__code/git/emailrak/elt_lake
claude
```

Then prompt:

```
Generate LeanIX diagram.net xml file for the workday integration from the SAD document: ~/Downloads/SAD_INT006_Barclaycard_Visa_Credit_Card_v1_0.docx
```

Claude will automatically:
1. Read the SKILL.md and recognise the request
2. Parse the SAD `.docx` using `python-docx` (via `uv run --package elt-doc-sad-leanix python ...`)
3. Extract integration ID, vendor name, direction, security details
4. Select the appropriate template (outbound EIB, bi-directional API, multi-connector, or via Hyve SFTP)
5. Generate a diagrams.net XML file saved alongside the input SAD document

The output XML can be imported directly into LeanIX.

## How It Works

This project is a **uv workspace member**. The workspace root is `elt_lake/`, and this module (`elt_doc_sad_leanix`) is one of its members alongside `elt_ingest_rest`.

The Claude Code skill (`.claude-code/skills/leanix-from-sad/SKILL.md`) tells Claude to run Python with:

```bash
uv run --package elt-doc-sad-leanix python <script.py>
```

The `--package` flag ensures this member's dependencies (`python-docx`, `openpyxl`) are installed in the shared workspace `.venv` before execution — regardless of which workspace member was synced first. No manual `uv sync` step is needed.

## Project Structure

```
elt_doc_sad_leanix/
├── pyproject.toml                              # python-docx, openpyxl dependencies
├── README.md
├── src/elt_doc_sad_leanix/
│   ├── __init__.py
│   ├── py.typed
│   ├── generate_integration_xml.py             # XML generator
│   ├── models/
│   └── parsers/
├── config/
│   └── LeanIX_Inventory.xlsx                   # LeanIX asset inventory
├── examples/
│   ├── COR_V00.01_INT001_Workday_Okta.xml      # bi-directional API
│   ├── COR_V00.01_INT002_Workday_Crisis24.xml   # outbound via Hyve SFTP
│   ├── COR_V00.01_INT004_AMEX_GBT.xml          # outbound to vendor SFTP
│   ├── COR_V00_01_INT006_Barclaycard.xml        # inbound via Hyve SFTP
│   └── COR_V00.01_INT018_Barclays_Banking.xml   # multi-connector complex
└── test/
```

## Running the Generator Directly

```bash
uv run --package elt-doc-sad-leanix python elt_doc_sad_leanix/src/elt_doc_sad_leanix/generate_integration_xml.py
```
