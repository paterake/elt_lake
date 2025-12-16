# Refactoring Plan: Modular Structure

## Current State
- **Single file**: `ingest_rest.py` (670 lines)
- Hard to understand flow and responsibilities
- All classes and logic mixed together

## Target Structure

```
src/elt_ingest_rest/
├── models/                          # Data classes (models)
│   ├── __init__.py
│   ├── pagination.py                # PaginationType, PaginationConfig
│   └── config.py                    # IngestConfig
│
├── parsers/                         # JSON parsing logic
│   ├── __init__.py
│   └── json_parser.py               # JsonConfigParser (from_json, to_json)
│
├── strategies/                      # Pagination strategy implementations
│   ├── __init__.py
│   ├── base.py                      # BasePaginationStrategy (abstract)
│   ├── none.py                      # NoPaginationStrategy
│   ├── offset_limit.py              # OffsetLimitStrategy
│   ├── page_number.py               # PageNumberStrategy
│   ├── cursor.py                    # CursorStrategy
│   ├── next_url.py                  # NextUrlStrategy
│   └── link_header.py               # LinkHeaderStrategy
│
├── ingester.py                      # Main orchestration class
├── __init__.py                      # Public API exports
└── ingest_rest.py                   # DEPRECATED (for backwards compat)
```

## Responsibilities

### 1. **models/** - Data Structures
- `PaginationType`: Enum of supported pagination types
- `PaginationConfig`: Pagination settings dataclass
- `IngestConfig`: Main configuration dataclass

**Purpose**: Define the shape of configuration data

### 2. **parsers/** - Configuration Loading
- `JsonConfigParser.from_json()`: Read JSON → IngestConfig
- `JsonConfigParser.to_json()`: Write IngestConfig → JSON

**Purpose**: Handle JSON serialization/deserialization

### 3. **strategies/** - Pagination Logic
Each strategy implements:
- `fetch(session, config) → list[dict]`: Fetch all pages of data

**Strategies**:
- `NoPaginationStrategy`: Single request
- `OffsetLimitStrategy`: ?offset=N&limit=M
- `PageNumberStrategy`: ?page=N&per_page=M
- `CursorStrategy`: ?cursor=TOKEN
- `NextUrlStrategy`: Follow response.next
- `LinkHeaderStrategy`: Follow Link: <url>; rel="next"

**Purpose**: Isolate pagination algorithms

### 4. **ingester.py** - Main Orchestration
`RestApiIngester` class:
1. Initialize HTTP session with retry logic
2. Select pagination strategy based on config
3. Delegate to strategy.fetch()
4. Save results to disk

**Purpose**: Coordinate the overall flow

## Process Flow (New Architecture)

```
┌─────────────────────────────────────────────┐
│  1. User provides JSON config               │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  2. JsonConfigParser.from_json()            │
│     - Load JSON from file/string/dict       │
│     - Validate structure                    │
│     - Convert types (str→enum, str→Path)    │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  3. IngestConfig dataclass created          │
│     - Contains all configuration            │
│     - Includes PaginationConfig             │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  4. RestApiIngester(config)                 │
│     - Setup HTTP session + retry logic      │
│     - Select strategy based on pagination   │
│       type                                  │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  5. Strategy.fetch(session, config)         │
│     ┌─────────────────────────────────┐    │
│     │ if NONE → NoPaginationStrategy   │    │
│     │ if OFFSET_LIMIT → OffsetLimit... │    │
│     │ if PAGE_NUMBER → PageNumber...   │    │
│     │ if CURSOR → CursorStrategy       │    │
│     │ if NEXT_URL → NextUrlStrategy    │    │
│     │ if LINK_HEADER → LinkHeader...   │    │
│     └─────────────────────────────────┘    │
│     - Make HTTP requests                    │
│     - Extract data from responses           │
│     - Return all collected data             │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  6. RestApiIngester.save()                  │
│     - Save to single JSON file OR           │
│     - Save to multiple batch files          │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  7. Return (data, output_path)              │
└─────────────────────────────────────────────┘
```

## Benefits

### ✅ Clarity
- Each file has ONE clear responsibility
- Process flow is obvious from file structure
- Easy to find where logic lives

### ✅ Maintainability
- Change pagination logic? Edit one strategy file
- Add new pagination type? Add one new strategy file
- Fix JSON parsing? Edit json_parser.py only

### ✅ Testability
- Test each strategy independently
- Mock strategies easily
- Test JSON parsing separately from ingestion

### ✅ Extensibility
- Add new pagination strategies without touching existing code
- Swap strategies dynamically
- Override strategies for custom behavior

## Migration Strategy

1. ✅ Create new modular structure
2. ✅ Keep `ingest_rest.py` importing from new modules (backwards compat)
3. ✅ Update `__init__.py` to export from both old and new
4. ✅ Run all tests - must pass without changes
5. Document new structure
6. Deprecate `ingest_rest.py` in future version

## Backwards Compatibility

```python
# Old import (still works)
from elt_ingest_rest import IngestConfig, RestApiIngester

# New import (preferred)
from elt_ingest_rest.models import IngestConfig
from elt_ingest_rest.ingester import RestApiIngester
```

Both work! No breaking changes for users.
