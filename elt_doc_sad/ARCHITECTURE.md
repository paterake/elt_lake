# elt-doc-sad Architecture

This module provides tooling for generating Solution Architecture Definition (SAD) documents following the FA standard template (**Solution Architecture Definition Template v2**).

## Core Idea

The SAD template defines a comprehensive structure for documenting integration architectures. This module:

- Encodes the template structure in configuration
- Provides content guidance based on existing SAD documents
- Generates SAD documents programmatically
- Validates SAD content completeness

## Prerequisites

### Source Documents

The module is based on:

1. **Solution Architecture Definition Template v2.docx** - The FA standard SAD template
2. **Existing SAD documents** (INT000-INT019) - Used to derive content guidance

### Template Structure

The template contains:

| Component | Count | Description |
|-----------|-------|-------------|
| Front Matter | 5 sections | Document History, Review, Approvals, References, Guidance |
| Main Sections | 8 sections | Introduction through Appendix |
| Subsections | 32 sections | Detailed topic areas |

### Cover Image

The template includes a cover page image (`cover_image.jpeg`) extracted from the Word document and stored in `resources/`.

## High-level Components

### Configuration
- `config/sad_template.json` - Document structure (front matter, sections, subsections)
- `config/section_guidance.json` - Content guidance for each section with examples
- `config/integration_patterns.json` - Common integration patterns (EIB, API, SFTP)

### Document Generation
- `src/elt_doc_sad/sad_generator.py` - Creates SAD documents from template

### Content Validation
- `src/elt_doc_sad/content_validator.py` - Validates SAD document completeness

### CLI Tools
- `src/elt_doc_sad/cmd/build_document.py` - Command-line document generation
- `src/elt_doc_sad/cmd/sad_pipeline.py` - Pipeline helper for automated workflows

## Configuration Model

### sad_template.json

Defines the **document structure**:

```json
{
  "version": "2.0",
  "front_matter": [
    {"name": "Document History", "type": "table", "required": true},
    {"name": "Document Review", "type": "table", "required": true},
    {"name": "Approvals", "type": "table", "required": true},
    {"name": "Reference Documents", "type": "list", "required": true},
    {"name": "Guidance", "type": "text", "required": false}
  ],
  "sections": {
    "1": {
      "title": "Introduction",
      "level": 1,
      "subsections": {
        "1.1": {"title": "Objectives", "required": true, "level": 2},
        "1.2": {"title": "Functionality", "required": true, "level": 2},
        "1.3": {"title": "Constraints", "required": true, "level": 2},
        "1.4": {"title": "Dependencies", "required": true, "level": 2},
        "1.5": {"title": "Legacy", "required": false, "level": 2}
      }
    }
    // ... sections 2-8
  }
}
```

### section_guidance.json

Provides **content guidance** for each section with:

- `description` - What the section should cover
- `should_include` - List of topics to include
- `example_topics` - Example content from existing SADs
- `typical_length` - Expected content length

Example:

```json
{
  "1.1 Objectives": {
    "description": "Primary objectives of implementing the integration",
    "should_include": [
      "Business goals the integration addresses",
      "Technical objectives",
      "Success criteria",
      "What is explicitly excluded from scope"
    ],
    "example_topics": [
      "Automated data provisioning",
      "Secure data transmission",
      "Compliance with data protection standards"
    ],
    "typical_length": "5-10 bullet points"
  }
}
```

### integration_patterns.json

Defines **common integration patterns** identified from existing SADs:

```json
{
  "patterns": {
    "outbound_eib_sftp": {
      "name": "Outbound EIB to SFTP",
      "description": "Workday → EIB → SFTP → Vendor",
      "components": ["EIB", "SFTP", "Vendor Endpoint"],
      "security": ["PGP Encryption", "SSH Key Authentication"],
      "examples": ["INT002 (Crisis24)", "INT003 (Headspace)"]
    }
  },
  "selection_criteria": {
    "use_outbound_eib_sftp_when": [
      "Workday is the source of truth",
      "Vendor provides SFTP endpoint",
      "Batch processing is acceptable"
    ]
  }
}
```

## Document Generation Flow

**Code:** `elt_doc_sad/src/elt_doc_sad/sad_generator.py`

### Steps

1. **Load Template Configuration**
   - Read `sad_template.json` for structure
   - Load `section_guidance.json` for content hints
   - Load cover image from `resources/cover_image.jpeg`

2. **Create Cover Page**
   - Add document title with integration ID and vendor name
   - Insert FA branding image

3. **Populate Front Matter**
   - Document History table (Version, Date, Author, Changes)
   - Document Review table (Name, Role, Date, Signature)
   - Approvals table (Name, Role, Date, Signature)

4. **Generate Sections**
   - For each of 8 main sections:
     - Create level-1 heading
     - For each subsection:
       - Create level-2 heading with number (e.g., "1.1 Objectives")
       - Add placeholder content with guidance hints

5. **Save Document**
   - Write to specified output path as `.docx`

## Content Validation Flow

**Code:** `elt_doc_sad/src/elt_doc_sad/content_validator.py`

### Steps

1. **Load SAD Document**
   - Parse Word document using `python-docx`
   - Extract all headings

2. **Check Required Sections**
   - Compare against `sad_template.json`
   - Identify missing required sections
   - Identify missing optional sections

3. **Calculate Completeness**
   - Count found sections vs total required
   - Generate percentage score

4. **Generate Report**
   - List found sections (✓)
   - List missing required sections (✗)
   - List missing optional sections (○)
   - Show completeness percentage

### Example Output

```
============================================================
SAD Document Validation Report
============================================================
Document: SAD_INT001_Okta_V1_0.docx
Valid: No
Completeness: 26.2%

Found Sections:
  ✓ Front Matter: Document History
  ✓ 1. Introduction
  ✓ 1.1 Objectives
  ...

Missing Required Sections:
  ✗ Front Matter: Reference Documents
  ✗ 2.1 GDPR
  ✗ 3.1 Security
  ...
============================================================
```

## Integration Patterns

Based on analysis of existing SAD documents (INT000-INT019):

### Pattern 1: Outbound EIB to SFTP

**Flow:** `Workday → [EIB Custom Report] → [CSV/XML] → [PGP Encrypt] → [SFTP] → Vendor`

**Used by:** INT002 (Crisis24), INT003 (Headspace), INT004 (AMEX GBT)

**Key characteristics:**
- EIB generates file on schedule
- Document Transformation for format conversion
- PGP encryption using vendor public key
- SFTP with SSH key authentication
- Vendor polls SFTP for files
- File purge after retrieval

### Pattern 2: Inbound from SFTP

**Flow:** `Vendor → [SFTP] → [Workday EIB Inbound] → [Document Transformation] → Workday`

**Used by:** INT008 (4me Payroll Inputs)

**Key characteristics:**
- Vendor drops file to FA-managed SFTP
- Workday EIB configured for inbound processing
- File validation before import
- Error handling for invalid records
- SSH key authentication from vendor

### Pattern 3: Bi-directional API

**Flow:** `Workday ↔ [REST API] ↔ [Vendor API] ↔ Vendor`

**Used by:** INT001 (Okta)

**Key characteristics:**
- OAuth 2.0 or API key authentication
- Scheduled polling (e.g., every 4 hours)
- Delta processing for efficiency
- Write-back capabilities (e.g., email addresses)
- Real-time or near-real-time sync

### Pattern 4: Multi-connector via FA SFTP

**Flow:** `Workday → [EIB] → [FA SFTP] → [Vendor SFTP Connection] → Vendor`

**Used by:** INT000 (Hyve Hosted SFTP)

**Key characteristics:**
- FA-managed SFTP as intermediary
- Vendor connects to FA SFTP from whitelisted IPs
- File purge after retrieval
- Comprehensive audit logging
- Multi-vendor distribution support

### Pattern 5: Outbound via FA SFTP

**Flow:** `Workday → [EIB] → [FA SFTP] → [Vendor Polling] → Vendor`

**Used by:** INT007 (4me Outbound)

**Key characteristics:**
- FA-hosted SFTP endpoint
- PGP encryption before delivery
- Vendor polling schedule
- Auto-purge after retrieval

## Section Content Guidance

Derived from analysis of existing SAD documents:

### Section 1: Introduction

| Subsection | Content | Examples |
|------------|---------|----------|
| 1.1 Objectives | Business goals, technical objectives, exclusions | "Automated provisioning", "GDPR compliance" |
| 1.2 Functionality | Components, data flow, scheduling | "EIB custom report", "Daily 6am schedule" |
| 1.3 Constraints | Compliance, technical, vendor limitations | "No test environment", "PGP required" |
| 1.4 Dependencies | Systems, configurations, data | "Workday HCM operational", "SSH keys exchanged" |
| 1.5 Legacy | Previous system, decommission plan | "PeopleXD → Workday transition" |

### Section 2: Data

| Subsection | Content | Examples |
|------------|---------|----------|
| 2.1 GDPR | Compliance controls, security measures | "Data minimization", "Encryption at rest" |
| 2.2 Sources | Source systems, data elements, scope | "Workday HCM", "Active employees only" |
| 2.3 Integration | Extraction, transformation, delivery | "EIB → CSV → PGP → SFTP" |
| 2.4 Migration | Initial load, cutover, validation | "Full load post go-live" |
| 2.5 Audit | Logging, retention, access | "180 days retention" |
| 2.6 Backups | Backup approach, recovery | "Workday stored outputs" |
| 2.7 Reporting | Monitoring, alerting | "Error notifications" |

### Section 3: Non-functional Requirements

| Subsection | Content | Examples |
|------------|---------|----------|
| 3.1 Security | ISU, ISSG, auth, encryption | "OAuth 2.0", "TLS 1.2+" |
| 3.2 Capacity | Volume, growth, peaks | "~700 employees", "10-50 daily changes" |
| 3.3 Performance | Processing times, retries | "Initial sync 30-60 min" |
| 3.4 Scalability | Growth capacity, expansion | "Supports 2-3x growth" |
| 3.5 Availability | SLA, maintenance, resilience | "99.7% Workday SLA" |
| 3.6 Disaster Recovery | RTO, RPO, recovery | "SaaS platform DR" |
| 3.7 Monitoring | Alerts, escalation, tools | "P1-P4 priorities" |

### Section 4: Solution Architecture

| Subsection | Content | Examples |
|------------|---------|----------|
| 4.1 Application Architecture | Pattern, components, flow | "Point-to-point", "8-step flow" |
| 4.2 Infrastructure Architecture | Hosting, network, firewall | "SaaS", "HTTPS port 443" |
| 4.3 Environments | Dev/test/prod, promotion | "Dev first, manual promotion" |
| 4.4 DevOps | Change management, testing | "Unit/functional/E2E testing" |

### Sections 5-8

| Section | Subsections | Content Summary |
|---------|-------------|-----------------|
| 5. Technology Stack | 5.1-5.3 | Protocols, data formats, tools |
| 6. Costs | 6.1-6.3 | Infrastructure, application, software costs |
| 7. Maintenance | 7.1-7.3 | Support model, roadmap, lifespan |
| 8. Appendix | 8.1-8.3 | Test scenarios, data mappings, security config |

## External Dependencies

### python-docx

- Word document creation and manipulation
- Style management for consistent formatting
- Table and image insertion
- Heading hierarchy management

### openpyxl

- Excel file handling for data mappings
- Reading LeanIX inventory spreadsheets
- Processing integration specification files

## File Structure

```
elt_doc_sad/
├── pyproject.toml                      # Dependencies: python-docx, openpyxl
├── README.md                           # Quick start (this file is detailed arch)
├── ARCHITECTURE.md                     # This detailed architecture document
├── src/elt_doc_sad/
│   ├── __init__.py                     # Package init
│   ├── py.typed                        # PEP 561 marker
│   ├── config_loader.py                # Load config files
│   ├── sad_generator.py                # Document generation
│   ├── content_validator.py            # Content validation
│   └── cmd/
│       ├── __init__.py
│       ├── build_document.py           # CLI: Build SAD
│       └── sad_pipeline.py             # CLI: Pipeline helper
├── config/
│   ├── sad_template.json               # Template structure
│   ├── section_guidance.json           # Content guidance per section
│   └── integration_patterns.json       # Integration patterns
├── resources/
│   └── cover_image.jpeg                # FA branding image
└── templates/
    └── sad_document.docx               # Optional base template
```

## Usage Examples

### Generate SAD with Default Settings

```bash
uv run --package elt-doc-sad python -m elt_doc_sad.sad_generator \
    --output-dir ./output \
    --integration-id INT001 \
    --vendor-name "Okta"
```

### Generate SAD with Custom Title

```bash
uv run --package elt-doc-sad python -m elt_doc_sad.sad_generator \
    --output-dir ./output \
    --integration-id INT003 \
    --vendor-name "Headspace" \
    --title "SAD_INT003_Headspace_Mental_Health_V1_0"
```

### Validate SAD Document

```bash
uv run --package elt-doc-sad python -m elt_doc_sad.content_validator \
    --input SAD_INT001_Okta_V1_0.docx \
    --report
```

### Validate Specific Section

```bash
uv run --package elt-doc-sad python -m elt_doc_sad.content_validator \
    --input SAD_INT001_Okta_V1_0.docx \
    --section 1.1
```

### Pipeline: Export Prompt for LLM

```bash
uv run --package elt-doc-sad python -m elt_doc_sad.cmd.sad_pipeline prompt \
    --output-dir .tmp/prompts \
    --integration-id INT001 \
    --vendor-name "Okta" \
    --pattern outbound_eib_sftp
```

## Extensibility

### Adding New Sections

Update `sad_template.json`:

```json
{
  "sections": {
    "9": {
      "title": "New Section",
      "level": 1,
      "subsections": {
        "9.1": {"title": "New Subsection", "required": true, "level": 2}
      }
    }
  }
}
```

### Adding Content Examples

Update `section_guidance.json` with examples from new SAD documents.

### Adding Integration Patterns

Update `integration_patterns.json`:

```json
{
  "patterns": {
    "new_pattern": {
      "name": "New Pattern Name",
      "description": "Source → Transform → Target",
      "components": [...],
      "security": [...],
      "examples": ["INTXXX"]
    }
  }
}
```

## Design Decisions

### Why Configuration-Driven?

- Template structure may evolve
- Different organizations may have variations
- Easy to add new sections without code changes
- Clear separation of structure vs. logic

### Why Placeholder Content?

- Generated SAD provides starting structure
- Users fill in integration-specific details
- Guidance hints help users understand what to include
- Validation ensures completeness before review

### Why Separate Validation?

- SAD documents require review before approval
- Automated validation catches missing sections
- Completeness score tracks progress
- Consistent structure across all SADs
