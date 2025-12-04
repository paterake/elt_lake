# JSON Configuration Architecture

## ✅ Proper Architecture Implemented

As requested, the JSON configuration support follows proper separation of concerns:

1. **`IngestConfig`** - Original dataclass (UNCHANGED)
2. **`IngestConfigJson`** - New JSON handler class (separate responsibility)

---

## 🏗️ Architecture Design

### Original Design (Unchanged)
```python
@dataclass
class IngestConfig:
    """Configuration for REST API ingestion."""
    base_url: str
    endpoint: str = ""
    method: str = "GET"
    # ... all original fields
```

**Purpose**: Hold configuration data
**Responsibility**: Data container (no I/O, no parsing)
**Status**: ✅ **UNCHANGED** - All existing code continues to work

### New JSON Handler (Separate Class)
```python
class IngestConfigJson:
    """JSON configuration handler for REST API ingestion."""

    @staticmethod
    def from_json(json_data) -> IngestConfig:
        """Load JSON and create IngestConfig."""
        # Parse JSON
        # Convert types
        # Return IngestConfig instance

    @staticmethod
    def to_json(config: IngestConfig) -> str:
        """Export IngestConfig to JSON."""
        # Extract config data
        # Convert to JSON
        # Return JSON string
```

**Purpose**: Handle JSON serialization/deserialization
**Responsibility**: I/O and type conversion
**Pattern**: Static methods (no state needed)

---

## 💡 Benefits of This Architecture

### 1. **Single Responsibility Principle**
- `IngestConfig` = Data structure
- `IngestConfigJson` = JSON I/O

### 2. **Open/Closed Principle**
- `IngestConfig` is closed for modification
- Extended functionality via new class

### 3. **Backwards Compatibility**
- All existing code works without changes
- No breaking changes to API

### 4. **Extensibility**
Easy to add more formats:
```python
class IngestConfigYaml:
    """YAML configuration handler."""
    @staticmethod
    def from_yaml(yaml_data) -> IngestConfig:
        # ...

class IngestConfigToml:
    """TOML configuration handler."""
    @staticmethod
    def from_toml(toml_data) -> IngestConfig:
        # ...
```

---

## 📝 Usage Examples

### Original Approach (Still Works)
```python
from elt_ingest_rest import IngestConfig, PaginationConfig, PaginationType

# Direct instantiation - unchanged
config = IngestConfig(
    base_url="https://api.example.com",
    endpoint="/data",
    pagination=PaginationConfig(
        type=PaginationType.PAGE_NUMBER,
        page_size=50
    )
)
```

### New JSON Approach
```python
from elt_ingest_rest import IngestConfigJson

# Load from JSON file
config = IngestConfigJson.from_json(Path("config.json"))

# Load from JSON string
config = IngestConfigJson.from_json('{"base_url": "..."}')

# Load from dict
config = IngestConfigJson.from_json({"base_url": "..."})
```

### Export to JSON
```python
from elt_ingest_rest import IngestConfig, IngestConfigJson

# Create config
config = IngestConfig(base_url="https://api.example.com")

# Export to JSON string
json_str = IngestConfigJson.to_json(config)

# Export to file
IngestConfigJson.to_json(config, Path("config.json"))
```

---

## 🔄 Type Conversion Flow

### Loading (JSON → IngestConfig)
```
JSON File/String/Dict
         ↓
IngestConfigJson.from_json()
         ↓
    Parse JSON
         ↓
Type Conversions:
  - "page_number" → PaginationType.PAGE_NUMBER
  - ["user", "pass"] → ("user", "pass")
  - "./output" → Path("./output")
         ↓
  IngestConfig(...)
         ↓
   Return config
```

### Saving (IngestConfig → JSON)
```
IngestConfig instance
         ↓
IngestConfigJson.to_json(config)
         ↓
Type Conversions:
  - PaginationType.PAGE_NUMBER → "page_number"
  - ("user", "pass") → ["user", "pass"]
  - Path("./output") → "./output"
         ↓
  JSON string/file
```

---

## 📊 Class Responsibilities

| Class | Responsibility | Contains |
|-------|---------------|----------|
| `IngestConfig` | Data structure | Fields, defaults, dataclass |
| `IngestConfigJson` | JSON I/O | `from_json()`, `to_json()` |
| `RestApiIngester` | API ingestion | HTTP requests, pagination |

**Clean separation**: Each class has one job!

---

## 🧪 Test Coverage

All tests pass with new architecture:

```bash
$ pytest test/test_json_config.py -v
======================== 14 passed in 0.40s =========================

$ pytest test/test_pagination_types.py -v
======================== 16 passed, 1 skipped in 4.14s ==============
```

- ✅ JSON loading tests
- ✅ JSON saving tests
- ✅ Roundtrip tests
- ✅ Integration tests
- ✅ Error handling tests
- ✅ Original Python API tests

---

## 📦 Exports

```python
# src/elt_ingest_rest/__init__.py
from .ingest_rest import (
    IngestConfig,          # Original
    IngestConfigJson,      # NEW
    PaginationConfig,
    PaginationType,
    RestApiIngester,
)
```

**Import styles:**
```python
# Import both
from elt_ingest_rest import IngestConfig, IngestConfigJson

# Or just what you need
from elt_ingest_rest import IngestConfigJson  # For JSON configs
from elt_ingest_rest import IngestConfig      # For Python configs
```

---

## 🎯 Design Patterns Used

### 1. **Separation of Concerns**
- Data (IngestConfig) separate from I/O (IngestConfigJson)

### 2. **Static Methods**
- No instance state needed
- `IngestConfigJson.from_json()` - factory method
- `IngestConfigJson.to_json()` - serializer method

### 3. **Factory Pattern**
- `from_json()` creates `IngestConfig` instances
- Handles multiple input formats (file/string/dict)

### 4. **Strategy Pattern (Future)**
- Easy to add more formats (YAML, TOML, XML)
- Each format handler is independent

---

## 🔍 Code Comparison

### Before (If we modified IngestConfig)
```python
@dataclass
class IngestConfig:
    # ... fields ...

    @classmethod
    def from_json(cls, json_data):  # ❌ Mixing concerns
        # JSON parsing logic mixed with data class
```

**Problems:**
- ❌ Mixed responsibilities
- ❌ IngestConfig knows about JSON
- ❌ Hard to add other formats
- ❌ Violates SRP

### After (Separate class)
```python
@dataclass
class IngestConfig:
    # ... fields only ...
    # ✅ Pure data structure

class IngestConfigJson:
    @staticmethod
    def from_json(json_data) -> IngestConfig:
        # ✅ JSON handling separate
```

**Benefits:**
- ✅ Clean separation
- ✅ IngestConfig doesn't know about JSON
- ✅ Easy to add YAML, TOML, etc.
- ✅ Follows SRP

---

## 🚀 Adding New Formats (Future)

With this architecture, adding new formats is trivial:

### YAML Support
```python
class IngestConfigYaml:
    """YAML configuration handler."""

    @staticmethod
    def from_yaml(yaml_data: str | Path) -> IngestConfig:
        import yaml
        if isinstance(yaml_data, Path):
            with open(yaml_data) as f:
                data = yaml.safe_load(f)
        else:
            data = yaml.safe_load(yaml_data)

        # Same conversion logic as JSON
        # ...
        return IngestConfig(**data)
```

### TOML Support
```python
class IngestConfigToml:
    """TOML configuration handler."""

    @staticmethod
    def from_toml(toml_data: str | Path) -> IngestConfig:
        import tomllib
        # ...
        return IngestConfig(**data)
```

**No changes needed to `IngestConfig`!**

---

## ✅ Validation Checklist

- [x] `IngestConfig` unchanged
- [x] New `IngestConfigJson` class created
- [x] Static methods (no instance state)
- [x] `from_json()` creates `IngestConfig`
- [x] `to_json()` exports `IngestConfig`
- [x] All original tests pass
- [x] All JSON tests pass
- [x] CLI script works
- [x] Backwards compatible
- [x] Follows SRP
- [x] Extensible design

---

## 📚 Summary

**Architecture Decision**: Separate JSON handling into dedicated class

**Rationale**:
1. Keep `IngestConfig` focused on data structure
2. Separate I/O concerns into `IngestConfigJson`
3. Make it easy to add more formats (YAML, TOML, etc.)
4. Maintain backwards compatibility
5. Follow SOLID principles

**Result**: Clean, maintainable, extensible architecture! ✨
