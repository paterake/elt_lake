# elt_doc_sad_leanix

Generate LeanIX diagrams.net XML files from Workday SAD (.docx) documents.

## Quick Start

### Step 1: Use the skill via Claude Code

```bash
cd /Users/rpatel/Documents/__code/git/emailrak/elt_lake
claude
```

Then prompt:

Create the LeanIX model from the SAD document
```
Generate LeanIX diagram.net xml file for the workday integration from the SAD document: ~/Downloads/SAD_INT006_Barclaycard_Visa_Credit_Card_v1_0.docx
```

Create the consolidated LeanIX model from the other LeanIX models
```
Now generate the consolidated overview LeanIX diagrams.net XML file.  Use the contents of ~/Downloads/leanix_workday_int, this folder holds all the required XML    
  files.  It includes the existing overview file called: COR_V00.01_INT000_Workday_Overview.xml, that was previously created (and this might need some correcting).   
  And then includes all the integrations between workday and vendors.  So review the existing overview, and either rebuild it from all the integrations or update     
  it - as required    
```  


Claude will automatically:
1. Read the SKILL.md and recognise the request
2. Parse the SAD `.docx` using `python-docx` (via `uv run --package elt-doc-sad-leanix python ...`)
3. Extract integration ID, vendor name, direction, security details
4. Select the appropriate template (outbound EIB, bi-directional API, multi-connector, or via FA SFTP)
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
├── templates/
│   ├── integration_bidirectional_api.xml         # Workday ↔ Vendor
│   ├── integration_outbound_fa_sftp.xml         # Workday → FA SFTP → Vendor
│   ├── integration_outbound_vendor_sftp.xml     # Workday → Vendor SFTP → Vendor
│   ├── integration_inbound_fa_sftp.xml          # Vendor → FA SFTP → Workday
│   ├── integration_multi_connector.xml          # Workday ↔ Gateway ↔ Vendor
│   └── integration_overview.xml                 # All integrations — summary overview
└── test/
```

## Running the Generator Directly

```bash
uv run --package elt-doc-sad-leanix python elt_doc_sad_leanix/src/elt_doc_sad_leanix/generate_integration_xml.py
```
