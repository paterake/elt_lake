# elt_ingest_rest Architecture

`elt_ingest_rest` is a config-driven REST ingestion module. It fetches data from an API (with pluggable pagination strategies), parses responses (JSON/CSV/XML), and writes results to disk.

Reference pattern (house standard): [`elt_ingest_excel/ARCHITECTURE.md`](file:///Users/rpatel/Documents/__code/git/emailrak/elt_lake/elt_ingest_excel/ARCHITECTURE.md)

## Module Layout

```text
elt_ingest_rest/
├── config/
│   └── ingest/                     # JSON configs (one per API use-case)
├── examples/
│   └── run_from_json.py            # Thin runner: load config, call ingester
├── src/elt_ingest_rest/
│   ├── ingester.py                 # Orchestrator: select strategy, fetch, save
│   ├── models/                     # Typed config + enums
│   ├── parsers/                    # JSON config parsing + validation
│   ├── strategies/                 # Pagination strategies (fetch loop logic)
│   ├── response_parsers/           # Response parsing (json/csv/xml)
│   ├── writers/                    # Output writing (currently JSON)
│   ├── http/                       # Session creation (retries, auth, headers)
│   └── templating/                 # Runtime template resolution (e.g. dates)
└── pyproject.toml
```

## Separation of Concerns

- `config/`: operational behaviour (endpoints, params, pagination tuning, output paths).
- `parsers/`: converts JSON config into typed models (normalization + validation).
- `ingester.py`: orchestrates ingestion using the parsed models.
- `strategies/`: implement pagination and request sequencing.
- `response_parsers/`: parse response payloads by format.
- `writers/`: handle output encoding and file layout.

## Runtime Flow

```text
runner → config parser → RestApiIngester → pagination strategy
      → HTTP session (retries/auth/headers)
      → response parser (json/csv/xml)
      → writer (single/batch JSON)
```

## Key Extension Points

- Pagination: add a new strategy under `strategies/` and map it in `RestApiIngester._select_strategy()`.
- Response formats: add a parser in `response_parsers/` and wire it in `response_parsers/parse.py`.
- Writers: add output writers in `writers/` and call them from `RestApiIngester.save()`.

