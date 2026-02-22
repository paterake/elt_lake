# elt-doc-sad

Generate Solution Architecture Definition (SAD) documents using the FA standard template.

## Quick Start

### Prerequisites

- Ollama running locally (for LLM-assisted content generation)
- SAD template document: `Solution Architecture Definition Template v2.docx`
- Cover image extracted from template (stored in `resources/`)

### Install

```bash
cd /Users/rpatel/Documents/__code/git/emailrak/elt_lake
uv sync
```

### Generate a SAD Document

```bash
uv run --package elt-doc-sad python -m elt_doc_sad.sad_generator \
    --output-dir ~/Documents/sad_documents \
    --integration-id INT001 \
    --vendor-name "Okta"
```

### Validate a SAD Document

```bash
uv run --package elt-doc-sad python -m elt_doc_sad.content_validator \
    --input SAD_INT001_Okta_V1_0.docx \
    --report
```

## Commands

| Command | Description |
|---------|-------------|
| `sad_generator` | Generate SAD document with placeholder sections |
| `content_validator` | Validate SAD completeness against template |
| `cmd.sad_pipeline` | Pipeline helper for automated workflows |
| `cmd.build_document` | Build SAD from specification |

## Configuration

| File | Description |
|------|-------------|
| `config/sad_template.json` | SAD structure (8 sections, 32 subsections) |
| `config/section_guidance.json` | Content guidance per section |
| `config/integration_patterns.json` | 5 integration patterns |

## Integration Patterns

| Pattern | Flow | Examples |
|---------|------|----------|
| `outbound_eib_sftp` | Workday → EIB → SFTP → Vendor | INT002, INT003, INT004 |
| `inbound_sftp` | Vendor → SFTP → Workday | INT008 |
| `bidirectional_api` | Workday ↔ API ↔ Vendor | INT001 |
| `multi_connector` | Workday → FA SFTP → Vendor | INT000 |
| `outbound_fa_sftp` | Workday → FA SFTP → Vendor | INT007 |

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed architecture, flows, and design decisions
- **[config/section_guidance.json](config/section_guidance.json)** - Content guidance for each section

## Related Modules

- `elt_doc_sad_leanix` - Generate LeanIX diagrams from SAD documents
- `elt_doc_leanix_overview` - Consolidate SAD data into LeanIX overview diagrams
