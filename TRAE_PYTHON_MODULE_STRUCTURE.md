# Python Module Structure (House Rules)

This document is the canonical source of truth for how Python modules are structured in this repository.

Reference implementation for the patterns described here:

- [`elt_ingest_excel/ARCHITECTURE.md`](file:///Users/rpatel/Documents/__code/git/emailrak/elt_lake/elt_ingest_excel/ARCHITECTURE.md)

## Non‑Negotiables

### 1) Every module is a uv project

- Must have a `pyproject.toml`
- Must run via `uv run --project . <command>`
- Dependencies are declared in `pyproject.toml` (and a lockfile if present)

### 2) Zero hardcoding of operational values (strict)

Operational values are anything that can vary between consumers, pipelines, environments, or tuning needs.

- All operational behaviour must be driven by config files under `config/`
- Code must remain reusable across multiple business processes without growing `if/elif/else` sprawl
- New behaviours are introduced by adding/changing config and/or adding a new module, not by adding nested branching to existing code
- Code-level defaults are only acceptable for safe technical fallbacks and must be overrideable in config

### 3) Config parsing is separate from config processing

- Parser modules load, validate, and normalize config into typed models
- Processing modules accept typed models and execute logic
- Processing modules do not open/read config files directly

### 4) Orchestrators coordinate; subtasks do the work

- A top-level orchestrator class owns the workflow and its phase ordering
- Each major activity lives in its own module(s)
- Orchestrator calls “down” to submodules; submodules do not call “up”

### 5) Runners are thin entrypoints

- Runner scripts live in `examples/` (or `src/<pkg>/cmd/` where appropriate)
- Runners only:
  - parse CLI args
  - locate/select config path(s)
  - load config via parser(s)
  - call the orchestrator and print a brief summary

## Recommended Repository Layout

```text
<module_name>/
├── config/
│   ├── ingest/                 # Ingest configs (one per pipeline)
│   ├── transform/              # Transform artifacts (SQL, order files, mappings)
│   ├── publish/                # Publish configs (one per pipeline)
│   └── data/                   # Static/reference data used by processing
├── examples/
│   ├── base_runner.py          # Shared CLI wiring (optional)
│   └── run_<pipeline>.py       # Thin runner(s)
├── src/<package_name>/
│   ├── __init__.py
│   ├── models/                 # Typed config + results
│   ├── parsers/                # Config parsing + validation
│   ├── reporting/              # Console summaries, metrics, etc.
│   ├── <phase_or_domain>/      # Implementation modules by concern
│   ├── <pipeline>.py           # Orchestrator(s)
│   └── py.typed                # If typed/distributed
├── test/ or tests/
└── pyproject.toml
```

## What Counts as Hardcoding (banned)

Hardcoding is any operational behaviour or value embedded in Python that should be tunable per consumer/pipeline. This includes:

- Endpoints and URLs, query params, headers, auth scheme selection
- Paths, filenames, directory layouts, file patterns, workbook/sheet/table names
- Pagination behaviour, record tags/paths, field mappings, schema rules
- Pipeline toggles that affect behaviour (which steps run, order, modes)
- Limits and tuning (batch sizes, concurrency, retries/backoff, timeouts)
- Business rules and transformations (these belong in SQL/config/mapping assets)

Allowed:

- Algorithmic logic and orchestration wiring
- Parsing/validation logic and type normalization
- Logging and error handling

## Avoiding Branching Sprawl

Goal: support multiple downstream processes without accumulating complex nested logic.

Preferred techniques:

- Strategy objects selected by config (pagination type, response format, writer type)
- Small, single-purpose executors invoked by an orchestrator
- Phase gating via a `PipelinePhase` enum and `run_to_phase` (and/or explicit skip controls)
- Explicit extension points (new module + schema) instead of global flags in core logic

## Multi‑Phase Pipelines (Run/Skip Semantics)

When a module performs several activities, model them as explicit phases (example: `INGEST → TRANSFORM → PUBLISH`):

- Phases are represented as an enum (e.g. `PipelinePhase`)
- Orchestrator enforces ordering and cumulative execution:
  - running `PUBLISH` implies `INGEST` and `TRANSFORM`
- The orchestrator supports running or skipping aspects of the process via config/CLI in a structured way (no scattered flags)
- Each phase implementation lives in its own module(s) and is testable independently

