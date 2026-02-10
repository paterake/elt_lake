# elt_doc_vendor_assess

Generate vendor assessment documents (.docx) for FA's supplier evaluation and ACB approval process.

## Quick Start

### Use the skill via Claude Code

```bash
cd /Users/rpatel/Documents/__code/git/emailrak/elt_lake
claude
```

Then prompt:

```
Evaluate vendors for SaaS SFTP solutions for Workday integration file transfers
```

Claude will automatically:
1. Read the SKILL.md and recognise the request
2. Search the web for vendors and compliance data
3. Classify vendors against FA's 4 mandatory security requirements
4. Generate a Vendor Compliance Matrix .docx with comparison tables and recommendation
5. Save the document to `~/Downloads/`

Follow up with:
```
Generate supplier selection questionnaire for Hyve Managed Hosting
```

And then:
```
Generate preferred technologies change for Hyve Managed SFTP Hosting
```

## Three Document Types

| Document | Purpose | Perspective |
|----------|---------|-------------|
| Vendor Compliance Matrix | Multi-vendor comparison with 8 tables | FA |
| Supplier Selection Questionnaire | 13-section vendor deep-dive | Vendor |
| Preferred Technologies Change | ACB approval request | FA |

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
│   ├── generate_compliance_matrix.py           # Doc type 1: Vendor Compliance Matrix
│   ├── generate_supplier_selection.py          # Doc type 2: Supplier Selection Questionnaire
│   └── generate_preferred_tech_change.py       # Doc type 3: Preferred Technologies Change
├── templates/                                  # Reference documents (structural examples)
│   ├── CRM_Migration_Tool_Compliance_Assessment.docx
│   ├── SaaS_SFTP_Compliance_Matrix.docx
│   ├── Supplier_Selection_Template.docx
│   ├── Preferred_Technologies_Change_Template.docx
│   ├── Preferred_Technologies_Change_Hyve_SFTP.docx
│   └── Supplier_Selection_Questionnaire_Hyve_completed.docx
└── test/
```

## Running Generators Directly

```bash
# Vendor Compliance Matrix
uv run --package elt-doc-vendor-assess python \
    elt_doc_vendor_assess/src/elt_doc_vendor_assess/generate_compliance_matrix.py \
    data.json output.docx

# Supplier Selection Questionnaire
uv run --package elt-doc-vendor-assess python \
    elt_doc_vendor_assess/src/elt_doc_vendor_assess/generate_supplier_selection.py \
    data.json output.docx

# Preferred Technologies Change
uv run --package elt-doc-vendor-assess python \
    elt_doc_vendor_assess/src/elt_doc_vendor_assess/generate_preferred_tech_change.py \
    data.json output.docx
```
