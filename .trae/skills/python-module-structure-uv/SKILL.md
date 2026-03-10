---
name: "python-module-structure-uv"
description: "Defines the house structure for Python modules (uv projects, config-driven, modular orchestration). Invoke when starting/refactoring a Python module or adding new pipeline stages."
---

# Python Module Structure (uv + Config-Driven)

Canonical source of truth

- Python module structure rules are defined once at:
  - `TRAE_PYTHON_MODULE_STRUCTURE.md`
- This skill does not duplicate the full rule text; it enforces the rules and applies them during implementation/refactors.
- Update `TRAE_PYTHON_MODULE_STRUCTURE.md` to change the house standard; this skill will follow that specification.

Canonical reference implementation for patterns and naming:

- [`elt_ingest_excel`](file:///Users/rpatel/Documents/__code/git/emailrak/elt_lake/elt_ingest_excel/ARCHITECTURE.md)

What this skill does (enforcement summary)

 - Enforces “uv project” structure and `uv run --project . ...` usage.
 - Enforces strict separation of concerns: config vs parsing vs processing vs orchestration.
 - Enforces zero hardcoding of operational values by moving behaviour into `config/`.
 - Implements multi-phase pipelines using orchestrator + phase enum when needed.

When to invoke

- Creating a new Python module/package in this repo.
- Refactoring a module that has mixed concerns, monolith files, or hardcoded behaviour.
- Adding a new pipeline phase, adding run/skip controls, or adding new config-driven workflows.

## Recommended Repository Layout

Use a consistent layout across modules (mirrors what works well in `elt_ingest_excel`):

```text
<module_name>/
├── config/
│   ├── ingest/                 # Ingest JSON configs (one per pipeline)
│   ├── transform/              # SQL, order files, mappings
│   ├── publish/                # Publish JSON configs (one per pipeline)
│   └── data/                   # Reference/static data used by processing
├── examples/
│   ├── base_runner.py          # Shared CLI wiring (optional)
│   └── run_<pipeline>.py       # Thin runner(s)
├── src/<package_name>/
│   ├── __init__.py
│   ├── models/                 # Typed config models + result models
│   ├── parsers/                # JSON/YAML/etc parsers + validation
│   ├── <phase_or_domain>/      # Implementation modules by concern
│   ├── reporting/              # Console summaries, metrics, etc.
│   ├── <pipeline>.py           # Orchestrator(s): pipeline entrypoints
│   └── py.typed                # If the module is typed/distributed
├── test/ or tests/
└── pyproject.toml
```

## Output Expectations (what to produce when invoked)

When invoked, do all of the following:

1. Propose a target directory structure
2. Identify concerns and split responsibilities (models/parsers/orchestrators/executors/writers/reporting)
3. Keep public API stable (if the module is already in use) via `__init__.py` exports
4. Move JSON config templates into `config/` and keep `examples/` as runners only
5. Update docs/tests/paths accordingly
6. Run:
   - `uv run --project . pytest -q` (module root)
   - repo-standard lint/format/typecheck commands (if present)

## Concrete Template: Thin Runner

Preferred runner behaviour:

```text
examples/run_from_json.py
- accepts a config path
- loads config via <package>.parsers
- instantiates orchestrator and calls .ingest() / .run() / .execute()
- prints summary (records count, output path)
```

Runners must not:

- embed default operational settings that belong in JSON
- implement parsing logic inline
- implement orchestration logic inline
