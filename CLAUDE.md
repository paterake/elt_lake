# Project Guidelines

## SQL Formatting Rules

This project’s SQL style is defined centrally in TRAE.md.

- See: TRAE.md → “SQL Formatting Rules (Trae)”
- The SQL formatting skill enforces those rules directly from TRAE.md.

## Python Environment

- Always run Python scripts with `uv run --package <package-name> python` from the workspace root.
- Do NOT use `cd <package> && uv run python` — this fails when the workspace venv was created by a different workspace member.

## LeanIX Diagram Skills

Two separate skills, each with its own code package and Claude skill definition.

### Skill 1: SAD-to-Diagram (`leanix-from-sad`)

- **Skill:** `.claude/skills/leanix-from-sad/SKILL.md`
- **Package:** `elt_doc_sad_leanix/`
- **Run with:** `uv run --package elt-doc-sad-leanix python`
- **LeanIX inventory:** `elt_doc_sad_leanix/config/LeanIX_Inventory.xlsx` — single flat sheet, filter by `type` column, two header rows, data starts at row 2
- **Key source files** (in `src/elt_doc_sad_leanix/`):
  - `cmd/build_xml.py` — JSON spec → XML builder CLI
  - `cmd/compile_context.py` — assembles LLM prompt from inventory + SAD
  - `prompts/sad_to_leanix.md` — LLM prompt template for JSON generation
  - `diagram_generator.py` — `WorkdayIntegrationDiagramGenerator` class
  - `legacy/generate_from_sad.py` — legacy heuristic SAD parsing
- **Output:** Save generated XML to same directory as input SAD `.docx`, same filename with `.xml` extension

### Skill 2: Overview Consolidation (`leanix-overview`)

- **Skill:** `.claude/skills/leanix-overview/SKILL.md`
- **Package:** `elt_doc_leanix_overview/`
- **Run with:** `uv run --package elt-doc-leanix-overview python`
- **Key source files** (in `src/elt_doc_leanix_overview/`):
  - `update_overview.py` — overview generator
  - `verify_overview.py` — validation script
  - `cmd/compile_context.py` — assembles LLM prompt from individual integration XMLs
  - `cmd/build_xml.py` — JSON spec → overview XML builder CLI
  - `prompts/consolidate_overview.md` — LLM prompt template for JSON generation
  - `templates/integration_overview.xml` — reference template
- **Does NOT need LeanIX inventory** — individual XMLs already contain resolved fact sheet IDs

### Shared Knowledge (Both Skills)

- **Four fact sheet types in diagrams:**
  - `Application` (blue `#497db0`) — boxes for BOTH Workday AND vendor systems; preferred for vendors
  - `Provider` (orange `#ffa31f`) — fallback for vendors without Application entries
  - `ITComponent` (brown `#d29270`) — infrastructure boxes (e.g. FA SFTP); no space in type value
  - `Interface` — applied to arrows/edges (not boxes); wraps edge mxCell in fact sheet object
- **Workday modules in LeanIX:** ONLY “Workday Human Capital Management” and “Workday Financial Management”
  - HCM: HR, identity, travel, demographics
  - FM: banking, payments, expenses, payroll settlement
- **XML generation:** When using `xml.etree.ElementTree`, pass raw HTML (with `<div>`) as attribute values — ET handles escaping. Pre-escaping causes double-escaping.
- **Multi-connector integrations:** `diagram_generator.py` detects `template_id: “multi_connector”` in JSON spec and generates a special three-box layout with 3 separate 2-column tables. Requires `sub_integrations` array in JSON spec.

## Environment Notes

- `analyze_compliance_docs.py` belongs in `elt_doc_vendor_assess/` (vendor assessment utility)
- `inspect_excel.py` stays in `elt_doc_sad_leanix/` (inventory inspection utility)
