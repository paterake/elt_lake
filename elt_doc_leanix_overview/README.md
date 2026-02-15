# elt_doc_leanix_overview

Consolidate multiple LeanIX integration diagrams into a single overview diagram.

## Quick Start

### Use the skill via Claude Code

```bash
cd /Users/rpatel/Documents/__code/git/emailrak/elt_lake
claude
```

Then prompt:

```
Create a new integration overview from the diagrams in ~/Downloads/leanix/
```

Claude will automatically:
1. Read the SKILL.md and recognise the request
2. Read all individual integration XML files from the directory
3. Extract integration data (vendors, protocols, volumes, security)
4. Generate a consolidated overview XML with aggregated notes
5. Save the overview XML

The output XML can be imported directly into LeanIX.

**For individual integration diagrams from SAD documents**, see the separate `elt_doc_sad_leanix` package and `leanix-from-sad` skill.

## Project Structure

```
elt_doc_leanix_overview/
├── pyproject.toml
├── README.md
├── src/elt_doc_leanix_overview/
│   ├── __init__.py
│   ├── update_overview.py                      # Overview generator (standalone)
│   ├── verify_overview.py                      # Overview validation
│   ├── cmd/
│   │   ├── build_xml.py                        # JSON spec → overview XML builder (CLI)
│   │   └── compile_context.py                  # Assembles LLM prompt from integration XMLs
│   └── prompts/
│       └── consolidate_overview.md             # LLM prompt template for JSON generation
├── templates/
│   └── integration_overview.xml                # Reference overview template
└── test/
```

## Trae LLM Pipeline

For use with Trae (or any LLM that accepts a compiled prompt):

```bash
# 1. Compile the prompt (integration XMLs + template → single markdown file)
uv run --package elt-doc-leanix-overview python elt_doc_leanix_overview/src/elt_doc_leanix_overview/cmd/compile_context.py ~/Downloads/leanix/

# 2. Feed output to LLM → get JSON spec back

# 3. Convert JSON spec → overview XML
uv run --package elt-doc-leanix-overview python elt_doc_leanix_overview/src/elt_doc_leanix_overview/cmd/build_xml.py overview_spec.json -o ~/Downloads/Workday_Integration_Overview.xml
```

For updating an existing overview:

```bash
# Include --existing flag to preserve current integrations
uv run --package elt-doc-leanix-overview python elt_doc_leanix_overview/src/elt_doc_leanix_overview/cmd/compile_context.py ~/Downloads/leanix/ --existing ~/Downloads/Workday_Overview.xml
```
