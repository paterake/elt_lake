# elt_doc_vendor_assess

Generate vendor assessment documents (.docx) for FA's supplier evaluation and ACB approval process.

## Quick Start

```bash
cd /Users/rpatel/Documents/__code/git/emailrak/elt_lake
claude
```

Then prompt through three phases:

```
Phase 1:  Evaluate vendors for SaaS SFTP solutions for Workday integration file transfers. I have provided an initial selection in ~/Downloads/sftp_vendors.txt
Phase 2:  Generate supplier selection questionnaire for Hyve Managed Hosting
Phase 3:  Generate preferred technologies change for Hyve Managed SFTP Hosting
```

## Three-Phase Assessment Workflow

The skill produces three documents in sequence. **The Compliance Matrix is the single source of truth** — all web research happens in Phase 1, and subsequent documents reuse that data without reassessment.

```
Phase 1                    Phase 2                      Phase 3
┌──────────────────┐       ┌──────────────────────┐     ┌─────────────────────────┐
│ Compliance Matrix│──────▶│ Supplier Selection    │────▶│ Preferred Technologies  │
│ (web research)   │       │ Questionnaire         │     │ Change                  │
│                  │       │ (reuses Phase 1 data) │     │ (reuses Phase 1+2 data) │
└──────────────────┘       └──────────────────────┘     └─────────────────────────┘
     FA perspective              Vendor perspective           FA perspective
     Multi-vendor comparison     Single vendor deep-dive      ACB approval request
```

### Phase 1: Vendor Compliance Matrix

- User can optionally supply an **input file** of initial vendor picks (one per line, e.g. `~/Downloads/vendors.txt`)
- Claude **always** also performs independent web research for additional candidates — the final list is the union of both
- Each vendor is researched for certifications, hosting, security, pricing
- Vendors are classified into 3 tiers against FA's 4 mandatory security requirements
- A single recommendation is made (primary + alternative + budget option)
- Output: `~/Downloads/Vendor_Compliance_Matrix_<category>_<date>.docx`

### Phase 2: Supplier Selection Questionnaire

- Uses the recommended vendor from Phase 1 (or a user-specified vendor from the matrix)
- Reuses all compliance data already gathered — no reassessment
- Supplementary web research only if specific questions need deeper answers
- 13 sections, 70+ sub-questions, written from the vendor's perspective
- Output: `~/Downloads/Supplier_Selection_Questionnaire_<vendor>_<date>.docx`

### Phase 3: Preferred Technologies Change

- Uses data from both Phase 1 and Phase 2
- Reuses all prior research — no reassessment
- Written from FA's perspective for ACB approval
- 11 sections + appendix, with the correct Security variant (SaaS/Application/Library) auto-selected
- Output: `~/Downloads/Preferred_Technologies_Change_<vendor>_<date>.docx`

## FA Mandatory Security Requirements

Every vendor is assessed against these 4 hard requirements:

| # | Requirement |
|---|-------------|
| 1 | ISO 27001 OR SOC 2 Type II certification |
| 2 | UK/EU data residency |
| 3 | Major Cloud Provider (AWS/Azure/GCP) OR Private Infrastructure |
| 4 | Panorays compatibility / demonstrated security best practices |

### 3-Tier Compliance Classification

| Tier | Classification | Criteria |
|------|---------------|----------|
| 1 | Fully Compliant | Meets all 4 mandatory requirements |
| 2 | Requires Review | Partial compliance, missing documentation |
| 3 | Non-Compliant | Fails one or more mandatory criteria |

## Conditional Document Sections

The Compliance Matrix is a superset of all reference examples. Sections and tables are included or excluded based on the product category:

| Section / Table | When Included |
|-----------------|---------------|
| Domain Context | Category requires business context (e.g. FX rates, payroll) |
| Incumbent Assessment | Replacing an existing solution |
| Overview Table | Always |
| ISO / SOC 2 Compliance Table | Always (columns adapt per category) |
| Security Features Table | Always (fields adapt per category) |
| Infrastructure & Cost Table | When hosting/cost comparison is relevant |
| Advanced Security Table | When advanced security features differ across vendors |
| GDPR Articles Table | When GDPR article-level compliance matters |
| SOC / HIPAA / Regulatory Table | When multiple regulatory frameworks apply |
| Tier 3 Summary Table | Automatically added when 3+ vendors are Tier 3 |

## Three Document Types

| Document | Generator | Perspective | Sections |
|----------|-----------|-------------|----------|
| Vendor Compliance Matrix | `generate_compliance_matrix.py` | FA | Conditional tables + tier assessment + recommendation |
| Supplier Selection Questionnaire | `generate_supplier_selection.py` | Vendor | 13 numbered sections with sub-questions |
| Preferred Technologies Change | `generate_preferred_tech_change.py` | FA | 11 sections + 3 Security variants (SaaS/App/Library) |

## How It Works

This project is a **uv workspace member**. The workspace root is `elt_lake/`, and this module (`elt_doc_vendor_assess`) is one of its members.

The Claude Code skill (`.claude-code/skills/vendor-assess/SKILL.md`) tells Claude to run Python with:

```bash
uv run --package elt-doc-vendor-assess python <script.py> <args>
```

The `--package` flag ensures this member's dependencies (`python-docx`) are installed in the shared workspace `.venv` before execution.

## Project Structure

```
elt_doc_vendor_assess/
├── pyproject.toml                              # python-docx dependency
├── README.md
├── src/elt_doc_vendor_assess/
│   ├── __init__.py
│   ├── py.typed
│   ├── generate_compliance_matrix.py           # Phase 1: Vendor Compliance Matrix
│   ├── generate_supplier_selection.py          # Phase 2: Supplier Selection Questionnaire
│   └── generate_preferred_tech_change.py       # Phase 3: Preferred Technologies Change
├── templates/                                  # Blank templates (structural reference)
│   ├── Compliance Matrix Template.docx         # Phase 1: full superset structure
│   ├── Supplier Selection Template.docx        # Phase 2: 13-section questionnaire
│   └── Preferred Technologies Change Template.docx  # Phase 3: ACB approval
└── test/
```

## Running Generators Directly

Each generator takes a JSON file and output path:

```bash
# Phase 1: Vendor Compliance Matrix
uv run --package elt-doc-vendor-assess python \
    elt_doc_vendor_assess/src/elt_doc_vendor_assess/generate_compliance_matrix.py \
    data.json output.docx

# Phase 2: Supplier Selection Questionnaire
uv run --package elt-doc-vendor-assess python \
    elt_doc_vendor_assess/src/elt_doc_vendor_assess/generate_supplier_selection.py \
    data.json output.docx

# Phase 3: Preferred Technologies Change
uv run --package elt-doc-vendor-assess python \
    elt_doc_vendor_assess/src/elt_doc_vendor_assess/generate_preferred_tech_change.py \
    data.json output.docx
```
