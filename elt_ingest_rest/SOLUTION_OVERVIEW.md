# elt_ingest_rest Solution Overview

## Goal

Provide a reusable, config-driven way to ingest data from REST APIs into local files, without hardcoding operational values in code. This keeps the same codebase usable across multiple consumers and business processes without accumulating complex branching logic.

## How It Works

- Configuration describes what to call (base URL, endpoint, parameters, auth) and how to paginate.
- The ingester creates a session with retry policy, selects a pagination strategy, fetches all records, then writes output to disk.
- Response parsing is format-specific (JSON/CSV/XML) and isolated from pagination logic.

## Zero Hardcoding Principle

Operational choices that can vary between use-cases live in config, not code:

- endpoints, query params, headers, auth selection
- pagination type and tuning (page size, cursor fields, next URL paths)
- response format parsing choices (json/csv/xml details)
- output layout (single vs batch, filenames, directories)

Code provides reusable orchestration and strategy patterns instead of case-specific logic.

## Adding a New API Ingestion

1. Create a new JSON config in `config/ingest/`.
2. Run the standard runner:

```bash
uv run --project . python examples/run_from_json.py config/ingest/<your_config>.json -v
```

3. Commit the config so other processes can reuse the same ingestion behaviour.

## Verification

Run the module tests:

```bash
uv run --project . pytest -q
```

