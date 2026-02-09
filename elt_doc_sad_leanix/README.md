# elt_doc_sad_leanix

Generate LeanIX diagrams.net XML files from Workday SAD (.docx) documents.

## Quick Start

### Step 1: Bootstrap the Python environment (one-off)

Run this once after cloning, or again if `.venv` is deleted or `pyproject.toml` dependencies change.

```bash
cd elt_doc_sad_leanix
uv sync
```

This creates a `.venv` directory and installs `python-docx` and other required libraries.

### Step 2: Use the skill via Claude Code

```bash
cd /Users/rpatel/Documents/__code/git/emailrak/elt_lake
claude
```

Then prompt:

```
"Generate LeanIX diagram.net xml file for the workday integration from the SAD document: ~/Downloads/SAD_INT006_Barclaycard_Visa_Credit_Card_v1_0.docx"
```

Claude will automatically:
1. Read the SKILL.md and recognise the request
2. Parse the SAD `.docx` using `python-docx` (via `cd elt_doc_sad_leanix && uv run python ...`)
3. Extract integration ID, vendor name, direction, security details
4. Select the appropriate template (outbound EIB, bi-directional API, multi-connector, or via Hyve SFTP)
5. Generate a diagrams.net XML file (e.g. `COR_V00_01_INT006_Barclaycard.xml`)

The output XML can be imported directly into LeanIX.

## How It Works

The Claude Code skill (`.claude-code/skills/leanix-from-sad/SKILL.md`) and this module are connected by a text instruction inside the SKILL.md:

```bash
cd elt_doc_sad_leanix && uv run python <script.py>
```

When Claude reads the SKILL.md it follows that instruction, which:
1. Changes into this module's directory
2. `uv run` finds the `.venv` folder (created by `uv sync` in Step 1) and runs Python using it
3. The script has access to `python-docx` because it's installed inside that `.venv`

Without Step 1, there is no `.venv` and the skill will fail.

## Project Structure

```
elt_doc_sad_leanix/
├── pyproject.toml                              # python-docx dependency
├── README.md
├── src/elt_doc_sad_leanix/
│   ├── __init__.py
│   ├── py.typed
│   ├── generate_integration_xml.py             # XML generator
│   ├── models/
│   └── parsers/
├── examples/
│   ├── COR_V00_01_INT006_Barclaycard.xml       # sample output
│   └── XML_GENERATION_SOLUTION.md              # solution reference
└── test/
```

## Running the Generator Directly

```bash
cd elt_doc_sad_leanix
uv run python src/elt_doc_sad_leanix/generate_integration_xml.py
```
