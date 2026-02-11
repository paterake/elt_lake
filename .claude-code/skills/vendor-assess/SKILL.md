# Vendor Assessment Skill

Generate vendor assessment documents (.docx) for FA's supplier evaluation and Architecture Change Board (ACB) approval process.

## Workflow

```
User prompt (category + optional input file of initial vendor picks)
        │
        ▼
  ┌─────────────┐    Read file     ┌──────────────────┐    python-docx    ┌────────────┐
  │ Identify     │ ──(if given)──► │ Merge user picks  │ ───────────────► │ .docx      │
  │ product need │                 │ + WebSearch for   │                  │ document   │
  └─────────────┘  WebSearch ────► │ additional vendors│                  └────────────┘
                                   └──────────────────┘
```

**One document per prompt.** The three document types are generated in sequence across separate prompts:

1. **Vendor Compliance Matrix** — compare multiple vendors side-by-side (web research happens here)
2. **Supplier Selection Questionnaire** — deep-dive on the recommended vendor (vendor perspective)
3. **Preferred Technologies Change** — ACB approval document (FA perspective)

**IMPORTANT: The Compliance Matrix is the single source of truth.** All web research and vendor assessment happens during step 1. Steps 2 and 3 **reuse the data and recommendation from the Compliance Matrix** — they do NOT perform a fresh reassessment. The recommended vendor from the Compliance Matrix feeds directly into the Supplier Selection and Preferred Tech Change documents.

---

## When to Use This Skill

Activate when the user asks to:
- "Evaluate vendors for …"
- "Compare vendors for …"
- "Create a vendor compliance matrix for …"
- "Generate supplier selection questionnaire for …"
- "Generate preferred technologies change for …"
- "Vendor assessment for …"
- "Which [product category] should we use?"

---

## Python Environment

This is a **uv workspace member** within the `elt_lake` workspace. Dependencies (`python-docx`) are declared in `elt_doc_vendor_assess/pyproject.toml`.

**Always run Python with:**
```bash
uv run --package elt-doc-vendor-assess python <script.py> <args>
```

The `--package` flag ensures `python-docx` is installed in the shared workspace `.venv` regardless of which workspace member was synced first. Do NOT use `cd elt_doc_vendor_assess && uv run python` — this fails when the venv was created by a different member.

### Generator scripts

| Document Type | Script |
|---|---|
| Vendor Compliance Matrix | `elt_doc_vendor_assess/src/elt_doc_vendor_assess/generate_compliance_matrix.py` |
| Supplier Selection Questionnaire | `elt_doc_vendor_assess/src/elt_doc_vendor_assess/generate_supplier_selection.py` |
| Preferred Technologies Change | `elt_doc_vendor_assess/src/elt_doc_vendor_assess/generate_preferred_tech_change.py` |

### Reference templates

Three blank templates in `elt_doc_vendor_assess/templates/` provide structural reference:

| Template | Type | Contents |
|---|---|---|
| `Compliance Matrix Template.docx` | Compliance Matrix | Full superset structure with all mandatory and optional sections, placeholder guidance text |
| `Supplier Selection Template.docx` | Supplier Selection | 13-section questionnaire with placeholder questions |
| `Preferred Technologies Change Template.docx` | Preferred Tech Change | 11-section ACB approval document with placeholder questions |

---

## Output Location

- Save all generated .docx files to `~/Downloads/`
- Filename format: `{DocumentType}_{Category}_{Date}.docx`
  - Example: `Vendor_Compliance_Matrix_SFTP_2026-02-10.docx`
  - Example: `Supplier_Selection_Hyve_2026-02-10.docx`
  - Example: `Preferred_Tech_Change_Hyve_SFTP_2026-02-10.docx`
- Do NOT save to the project directory
- Do NOT create intermediate/throwaway Python scripts — write JSON data to a temp file and pass it to the generator

---

## FA Mandatory Security Requirements

Every vendor is assessed against these 4 hard requirements. **All 4 must be met** for Tier 1 (Fully Compliant) status.

1. **ISO 27001 OR SOC 2 Type II** — minimum one certification required
2. **UK/EU data residency** — data must be stored/processed in UK or EU
3. **Major Cloud Provider OR Private Infrastructure** — must run on AWS, Azure, GCP, or own private infrastructure
4. **Panorays compatibility / demonstrated security best practices** — must support FA's third-party risk management process

### 3-Tier Compliance Classification

| Tier | Label | Criteria |
|------|-------|----------|
| 1 | **FULLY COMPLIANT** | Meets all 4 mandatory requirements |
| 2 | **REQUIRES REVIEW** | Partial compliance or missing documentation |
| 3 | **NON-COMPLIANT** | Fails one or more mandatory criteria (retired product, missing certs, non-UK/EU hosting) |

---

## Document Type 1: Vendor Compliance Matrix

### Purpose
Compare multiple vendors side-by-side across security, compliance, cost, and capability dimensions. Ends with a single primary recommendation.

### Document Structure

```
Title
├── Executive Summary
├── Recommended Vendor: [name]
│   ├── Key Strengths
│   ├── Contracted Deployment Configuration (if known)
│   └── Service Level Commitments (if known)
├── [Integration / Domain Context] (CONDITIONAL — when useful)
│   ├── Requirements specific to this product category
│   └── Key integration notes
├── [Incumbent / Platform Vendor Assessment] (CONDITIONAL — when applicable)
│   └── Table: why the obvious vendor is not suitable
├── Strategic Alignment with FA Preferred Technologies
│   ├── Relevant Technology Classifications
│   ├── Scope Definition
│   └── Justification
├── FA Security Mandatory Requirements
├── Vendor Compliance Matrix
│   ├── Table: Provider Overview & Capabilities (ALWAYS)
│   ├── Table: ISO/SOC 2 Compliance Matrix (ALWAYS)
│   ├── Table: Security Features Matrix (ALWAYS)
│   ├── Table: Infrastructure & Cost Comparison (when cost data available)
│   ├── Table: Advanced Security Features (when relevant — e.g. SFTP, file transfer)
│   ├── Table: GDPR Article Compliance (when handling personal data)
│   └── Table: SOC 2, HIPAA & Regional Compliance (when multiple regulatory frameworks apply)
├── FA Security Compliance Assessment
│   ├── Tier 1 — FULLY COMPLIANT (with per-vendor detail)
│   ├── Tier 2 — REQUIRES REVIEW
│   ├── Tier 3 — NON-COMPLIANT (with summary table)
│   └── Table: Vendor Compliance Summary (ALWAYS)
├── Recommendations Summary
├── Conclusion
├── Certification Methodology Note
└── Verification Sources
```

### Conditional Sections

**Integration / Domain Context** — Include when the product category has specific integration requirements that inform the assessment. For example: "Workday Integration Context" for FX rate providers (rate types, integration patterns), or "Workday HCM/Financials File Transfer Requirements" for SFTP assessments. Omit for generic product assessments.

**Incumbent / Platform Vendor Assessment** — Include when the user's existing platform has an expected capability that should be evaluated and ruled out (e.g. "Does Microsoft provide an FX rate API?", "Can Azure Blob Storage serve as managed SFTP?"). Present as a table showing each platform option, its limitation, and why it's not suitable. Omit when there's no obvious incumbent to address.

### Table Specifications

Tables should adapt to the product category. Not every assessment needs all table types. The three core tables (Overview, ISO/SOC 2, Security Features) are always included. The rest are conditional.

#### Core Tables (always include)

**Provider Overview & Capabilities**
Core columns: Vendor, Tool/Product Name, Tool Type, Deployment, Maturity
Add domain-specific columns as needed — e.g. for FX rate providers: "Daily Rates", "Monthly Avg", "Currencies", "Workday Integration". For SFTP: "Protocols Supported", "Max File Size".

**ISO/SOC 2 Compliance Matrix**
Core columns: Vendor, ISO 27001, SOC 2 Type II, GDPR, Compliance Route
The "Compliance Route" column is important — it shows whether compliance is "Direct", "Via Parent" (inherited from parent company), "Via [cloud provider]" (inherited from AWS/Azure), "Public Institution", or "No Public Docs".
Add additional certification columns when relevant to the category — e.g. ISO 27017/27018 for cloud services, SOC 1 for financial services, PCI DSS for payment processing.

**Security Features Matrix**
Columns adapt to the product category:
- For SFTP/file transfer: RBAC, SSH Key Mgmt, MFA/2FA, Encryption at Rest, Encryption Transit, IP Whitelisting, Tenancy Model
- For API services: Encryption Transit, API Auth method, Rate Limiting, Infrastructure, UK/EU Data
- For SaaS platforms: RBAC, SSO, MFA, Encryption at Rest/Transit, Audit Logging, Tenancy Model

#### Conditional Tables (include when relevant)

**Infrastructure & Cost Comparison** — Include when cost data is available for most vendors.
Columns: Vendor, Cloud/Infrastructure, UK/EU Hosting, Est. Annual Cost, Setup Cost, First Year Total

**Advanced Security Features** — Include for infrastructure products (SFTP, hosting, file transfer) where advanced security matters.
Columns: Vendor, IP Whitelisting, Data Archiving, Auto Purging, Audit Logging, Log Retention, DLP, Malware Scan, EDR

**GDPR Article Compliance** — Include when the product handles personal data (HR, CRM, identity).
Columns: Vendor, Art. 5,6 (Lawfulness), Art. 15,17 (Rights), Art. 25 (By Design), Art. 30 (Records), Art. 32 (Security), Art. 33 (Breach)

**SOC 2, HIPAA & Regional Compliance** — Include when multiple regulatory frameworks apply.
Columns: Vendor, SOC 2 Type II, HIPAA, PCI DSS, FedRAMP, CCPA, ITAR

**Incumbent / Platform Vendor Assessment Table** — Include when ruling out an obvious vendor choice.
Columns: Service/Product, Description, Limitation, Compatible with FA requirements?

**Tier 3 Non-Compliant Summary Table** — Include when there are 3+ non-compliant vendors to avoid verbose prose.
Columns: Provider, Assessment Notes, Status

#### Always-Last Table

**Vendor Compliance Summary** — Always the final table, summarising the assessment.
Core columns: Vendor, ISO/SOC 2, UK/EU Data, Infrastructure, Status
Add a domain-relevant column — e.g. "Workday" (Pre-built/Supported/Custom), "Panorays", or other key differentiator.
Status values: COMPLIANT (green), REVIEW (amber), NON-COMPLIANT (red)

### Notation Rules
- ✓ = Confirmed/Present (direct certification)
- ✗ = Not present/Failed
- — = Not applicable
- "Direct" = Vendor holds certification directly
- "Via Parent" = Inherited from parent company (e.g. "Via Euronet Worldwide")
- "Via [provider]" = Inherited from cloud/infrastructure provider (e.g. "Via AWS")
- "N/A — Public" = Not applicable for public institutions (e.g. ECB)
- "Unknown" = Could not be verified from public sources
- "No Public Docs" = Vendor has no publicly available compliance documentation
- "TBC" = To be confirmed with vendor directly

### Recommendation Format
Always include:
- **PRIMARY RECOMMENDATION:** Best Tier 1 vendor with justification
- **ALTERNATIVE RECOMMENDATION:** Second-best Tier 1 vendor (if available)
- **BUDGET OPTION:** Lower-cost compliant alternative (if available)

### JSON Input Schema

Pass data as a JSON file to the generator. Structure your JSON following the docstring in `generate_compliance_matrix.py`. Key fields:

```json
{
    "title": "...",
    "category": "...",
    "executive_summary": "...",
    "strategic_context": { ... },
    "mandatory_requirements": { "intro": "...", "requirements": [...] },
    "vendors": [ { "name": "...", "iso_27001": true, ... } ],
    "recommended_vendor": { "name": "...", "key_strengths": [...] },
    "tier_assessments": { "tier_1": [...], "tier_2": [...], "tier_3": [...] },
    "recommendations_summary": "...",
    "conclusion": "...",
    "verification_sources": [{ "vendor": "...", "url": "..." }]
}
```

### Generation Command
```bash
uv run --package elt-doc-vendor-assess python \
    elt_doc_vendor_assess/src/elt_doc_vendor_assess/generate_compliance_matrix.py \
    /tmp/matrix_data.json \
    ~/Downloads/Vendor_Compliance_Matrix_SFTP_2026-02-10.docx
```

---

## Document Type 2: Supplier Selection Questionnaire

### Purpose
A detailed vendor questionnaire filled with researched answers. Written from the **vendor's perspective** (as if the vendor is answering FA's questions).

### Document Structure

```
Title: Supplier Selection Questionnaire — [Vendor] ([Product])
├── Document History (table)
├── Reference Documents (table)
├── 1. Functionality
│   ├── 1.1 Core Functionality Overview
│   ├── 1.2 Use Case Diagram
│   └── 1.3 Architecture Context
├── 2. Extension
│   └── 2.1 Customization Capabilities
├── 3. Data
│   ├── 3.1 Data Held
│   ├── 3.2 Data Classification
│   ├── 3.3 Data Protection
│   └── 3.4 Testing Results
├── 4. AI
│   ├── 4.1 Model Training
│   ├── 4.2 Data Leaving Tenant
│   ├── 4.3 External AI Vendors
│   ├── 4.4 Bias Mitigation
│   ├── 4.5 GDPR & AI
│   ├── 4.6 EU AI Act
│   ├── 4.7 AI Transparency
│   ├── 4.8 Human Oversight
│   ├── 4.9 Data Quality for AI
│   ├── 4.10 Risk Assessment
│   └── 4.11 AI Documentation
├── 5. Security
│   ├── 5.1 SaaS Hosting
│   ├── 5.2 Shared or Dedicated
│   ├── 5.3 Penetration Testing
│   ├── 5.4 Vulnerability Scanning
│   ├── 5.5 Patching
│   ├── 5.6 Authentication
│   ├── 5.7 Admin Access
│   ├── 5.8 Vendor Data Access
│   ├── 5.9 Encryption
│   ├── 5.10 Intrusion Detection
│   ├── 5.11 Breach History
│   ├── 5.12 Security Frameworks
│   ├── 5.13 High Availability
│   └── 5.14 Backup & Recovery
├── 6. Performance
│   ├── 6.1 Scalability
│   ├── 6.2 Performance Benchmarks
│   ├── 6.3 SLAs
│   └── 6.4 SLA Enforcement
├── 7. Compliance and Regulations
│   ├── 7.1 Regulatory Compliance
│   └── 7.2 Certifications
├── 8. Reliability
│   ├── 8.1 Incident History
│   ├── 8.2 Observability
│   ├── 8.3 Disaster Recovery Plan
│   ├── 8.4 RPO
│   ├── 8.5 RTO
│   ├── 8.6 Failure Testing
│   └── 8.7 Integration Reliability
├── 9. Hosting
│   ├── 9.1 Hosting Location
│   ├── 9.2 Infrastructure Details
│   └── 9.3 Environments
├── 10. Technology
│   ├── 10.1 Technology Stack
│   ├── 10.2 Patching Strategy
│   ├── 10.3 Release Strategy
│   ├── 10.4 Breaking Changes
│   └── 10.5 Vulnerability Reporting
├── 11. Integration and API
│   ├── 11.1 Integration Options
│   ├── 11.2 Documentation
│   └── 11.3 Data Migration
├── 12. Roadmap
│   └── 12.1 Planned Releases
└── 13. Appendix
```

### Answer Guidelines
- Write answers as if the vendor is responding
- If the product does not use AI, answer AI section questions with "AI is not used in this product" — do not leave blank
- For information that cannot be verified via public sources, write "TBC — not publicly available; to be confirmed with vendor directly"
- Prefer substantive multi-paragraph answers over single sentences
- Include specific product names, versions, and technical details where available

### JSON Input Schema

See the docstring in `generate_supplier_selection.py` for the full structure. Key pattern:

```json
{
    "vendor_name": "...",
    "product_name": "...",
    "document_history": [{ "version": "1.0", "date": "...", "author": "...", "summary": "..." }],
    "reference_documents": [{ "document": "...", "link": "..." }],
    "sections": {
        "functionality": { "core_functionality": "...", "use_case_diagram": "...", "architecture_diagram": "..." },
        "extension": { "customization": "..." },
        "data": { ... },
        "ai": { ... },
        "security": { ... },
        "performance": { ... },
        "compliance": { ... },
        "reliability": { ... },
        "hosting": { ... },
        "technology": { ... },
        "integration_api": { ... },
        "roadmap": { ... },
        "appendix": "..."
    }
}
```

### Generation Command
```bash
uv run --package elt-doc-vendor-assess python \
    elt_doc_vendor_assess/src/elt_doc_vendor_assess/generate_supplier_selection.py \
    /tmp/supplier_data.json \
    ~/Downloads/Supplier_Selection_Hyve_2026-02-10.docx
```

---

## Document Type 3: Preferred Technologies Change

### Purpose
Request ACB approval to add a new technology to FA's Preferred Technologies list. Written from **FA's perspective** (the team authoring the justification, not the vendor).

### Technology Types
The document has three Security sections — only complete the one matching the technology type:
- **SaaS** — cloud-hosted service (Section 3: Security — SaaS Product)
- **Application** — locally installed application (Section 4: Security — Application)
- **Library** — code library or component (Section 5: Security — Library or Component)

Mark the other two Security sections as "N/A — this is a [type] product."

### Document Structure

```
Title: Preferred Technologies Change — [Technology Name]
├── Document History (table)
├── Reference Documents (table)
├── 1. Functionality
│   ├── 1.1 Key Features
│   ├── 1.2 Benefits vs. Competitors
│   └── 1.3 Advantages over Existing Mainstream
├── 2. Fit
│   ├── 2.1 Interoperability
│   └── 2.2 Customization
├── 3. Security — SaaS Product (14 sub-questions)
├── 4. Security — Application (10 sub-questions)
├── 5. Security — Library or Component (2 sub-questions)
├── 6. Versioning
│   └── 6.1 Version Control
├── 7. Hosting
│   └── 7.1 Infrastructure Requirements
├── 8. Maintenance
│   ├── 8.1 Roadmap
│   ├── 8.2 Release Cycle
│   └── 8.3 Upgrade Process
├── 9. Knowledge
│   └── 9.1 Training Requirements
├── 10. Implementation
│   ├── 10.1 Implementation Plan
│   ├── 10.2 Decommissioning Plan
│   └── 10.3 Migration Activities
├── 11. Costs
│   ├── 11.1 Licensing Costs
│   └── 11.2 Upgrade & Support Costs
└── Appendix
```

### Writing Style
- Write from FA's perspective — "We evaluated...", "The FA requires...", "This technology..."
- Section 1.3 must explicitly compare against the **existing Mainstream technology** and justify why a new addition is needed
- Section 10.1 should include a week-by-week implementation timeline where possible
- Section 11 should include specific GBP costs with annual recurring and first-year totals
- Reference the Compliance Matrix document and Supplier Selection Questionnaire where applicable

### JSON Input Schema

See the docstring in `generate_preferred_tech_change.py` for the full structure.

### Generation Command
```bash
uv run --package elt-doc-vendor-assess python \
    elt_doc_vendor_assess/src/elt_doc_vendor_assess/generate_preferred_tech_change.py \
    /tmp/tech_change_data.json \
    ~/Downloads/Preferred_Tech_Change_Hyve_SFTP_2026-02-10.docx
```

---

## Web Research Workflow

Use Claude's built-in `WebSearch` tool for all vendor research. Do NOT write custom Python web scraping code.

### Phase 1: Vendor Discovery

The user may supply an **input file** (e.g. `~/Downloads/vendors.txt`) containing their initial selection of vendors/products to review. If provided, read the file first — each line is a vendor or product name.

**Always** also perform independent web research to identify additional candidates. The final vendor list is the **union** of the user's picks and Claude's research — the user's picks are guaranteed to be included, not replaced.

Search for additional candidates (aim for 5-10 total including user picks):
- `"best [category] vendors 2026"`
- `"[category] comparison enterprise"`
- `"[category] for enterprise UK"`
- `"[category] ISO 27001 SOC 2"`

### Phase 2: Per-Vendor Compliance Research (for Compliance Matrix)
For each vendor, search:
- `"[vendor] ISO 27001 certification"` — check trust page / certification registries
- `"[vendor] SOC 2 Type II report"` — check if available / auditor name
- `"[vendor] GDPR compliance"` — DPA availability, data processing agreements
- `"[vendor] UK data centre"` or `"[vendor] EU hosting"` — hosting locations
- `"[vendor] pricing"` or `"[vendor] cost"` — licensing model and pricing
- `"[vendor] security whitepaper"` or `"[vendor] trust center"` — security documentation
- `"[vendor] Panorays"` — third-party risk management compatibility

### Phase 3: Supplementary Research (for Supplier Selection / Preferred Tech Change — only if needed)

The Compliance Matrix already contains the core vendor data. Only perform **targeted supplementary searches** if the Compliance Matrix data is insufficient to answer a specific section question (e.g. detailed roadmap, architecture diagrams, or implementation timeline specifics). Do NOT repeat the compliance/security/cost research — reuse what was already gathered.

If supplementary searches are needed:
- Product documentation pages and API docs
- Architecture and infrastructure details
- Release cadence, changelog, roadmap
- Integration options and supported protocols

### Sourcing Discipline
- **Cite sources** for all compliance claims in the document
- **Mark unverifiable claims** as "TBC — not publicly available"
- **Prefer** vendor trust pages and certification registries over marketing material
- **Distinguish** "Direct" certifications from "Inherited" (via AWS/Azure/IaaS provider)
- Include a **Verification Sources** section at the end of the Compliance Matrix with URLs

---

## Skill Execution Steps

### For Vendor Compliance Matrix

1. **Parse user request** — identify the product category, use case, and whether an input file of initial vendors was provided
2. **Build vendor list** — if the user supplied an input file, read it first (one vendor/product per line). Then **always** WebSearch for additional candidates. Merge both lists (deduplicate). The user's picks are always included.
3. **Research each vendor** — use WebSearch to gather compliance, security, hosting, and cost data
4. **Build vendor data objects** — for each vendor, populate all fields needed for the 8 tables
5. **Classify tiers** — apply the 4 FA mandatory requirements:
   - Check ISO 27001 OR SOC 2 Type II → pass/fail
   - Check UK/EU data residency → pass/fail
   - Check cloud provider / private infrastructure → pass/fail
   - Check Panorays / security best practices → pass/fail
   - All 4 pass = Tier 1, partial = Tier 2, any fail = Tier 3
6. **Select recommendation** — choose primary (best Tier 1), alternative (second Tier 1), budget option
7. **Write JSON data file** to `/tmp/` with all vendor data and narrative sections
8. **Run generator:**
   ```bash
   uv run --package elt-doc-vendor-assess python \
       elt_doc_vendor_assess/src/elt_doc_vendor_assess/generate_compliance_matrix.py \
       /tmp/matrix_data.json \
       ~/Downloads/Vendor_Compliance_Matrix_{Category}_{Date}.docx
   ```
9. **Clean up** — delete the temp JSON file
10. **Present results** — show the user a summary with tier breakdown and recommendation

### For Supplier Selection Questionnaire

**Prerequisite:** A Compliance Matrix must already exist for this product category. The recommended vendor from that matrix is the subject of this document.

1. **Identify the vendor** — use the primary recommendation from the Compliance Matrix (or user override)
2. **Reuse Compliance Matrix data** — extract the vendor's compliance, security, hosting, cost, and certification data already gathered during the matrix phase
3. **Targeted supplementary research** — only WebSearch for information not already in the matrix (e.g. detailed architecture, API documentation, release roadmap, AI usage). Do NOT re-research compliance/security/cost
4. **Fill all sections** — write answers from the vendor's perspective, drawing primarily from Compliance Matrix data
5. **Write JSON data file** to `/tmp/`
6. **Run generator:**
   ```bash
   uv run --package elt-doc-vendor-assess python \
       elt_doc_vendor_assess/src/elt_doc_vendor_assess/generate_supplier_selection.py \
       /tmp/supplier_data.json \
       ~/Downloads/Supplier_Selection_{Vendor}_{Date}.docx
   ```
7. **Clean up** and present results
8. **Reference documents** — include the Compliance Matrix .docx path in the reference documents table

### For Preferred Technologies Change

**Prerequisite:** Both the Compliance Matrix and (ideally) Supplier Selection Questionnaire should already exist. This document synthesises their findings into an ACB approval request.

1. **Identify the technology** — use the primary recommendation from the Compliance Matrix
2. **Determine technology type** — SaaS, Application, or Library
3. **Reuse existing data** — draw security answers from the Compliance Matrix tables, and detailed product information from the Supplier Selection Questionnaire. Do NOT re-research what was already gathered
4. **Targeted supplementary research** — only WebSearch for Preferred Tech Change–specific topics not covered in earlier documents (e.g. competitive comparison against the existing Mainstream technology, implementation timeline specifics, training requirements)
5. **Fill all sections** — write from FA's perspective, marking irrelevant Security sections as N/A
6. **Write JSON data file** to `/tmp/`
7. **Run generator:**
   ```bash
   uv run --package elt-doc-vendor-assess python \
       elt_doc_vendor_assess/src/elt_doc_vendor_assess/generate_preferred_tech_change.py \
       /tmp/tech_change_data.json \
       ~/Downloads/Preferred_Tech_Change_{Technology}_{Date}.docx
   ```
8. **Clean up** and present results
9. **Reference documents** — include both the Compliance Matrix and Supplier Selection .docx paths in the reference documents table

---

## Standard Response Pattern

After generating any document, present to the user:

```
### [Document Type] Generated

**Document:** ~/Downloads/[filename].docx

**Summary:**
- [Key finding 1]
- [Key finding 2]
- [Key finding 3]

**[Recommendation / Next Steps]:**
[For Compliance Matrix: Primary recommendation with justification]
[For Supplier Selection: Key observations about the vendor]
[For Preferred Tech Change: Readiness assessment for ACB submission]

**Sources consulted:**
- [Source 1 URL]
- [Source 2 URL]

**Next document:** [Suggest the next document type — e.g. "To continue, ask me to generate the Supplier Selection Questionnaire for [recommended vendor]"]
**Note:** The next document will build on the data already gathered — no reassessment needed.
```

---

## Critical Success Factors

1. **Accuracy** — only assert compliance claims that can be verified via public sources
2. **TBC marking** — flag anything that cannot be verified as "TBC — not publicly available"
3. **Source citation** — include verification URLs for all compliance data
4. **Direct vs Inherited** — distinguish vendor's own certifications from those inherited via cloud provider
5. **No throwaway scripts** — use temp JSON files, not intermediate Python scripts
6. **Consistent formatting** — all documents use Calibri font, Table Grid style, dark blue header rows
7. **One document per prompt** — do not generate multiple documents in a single response
8. **FA perspective vs vendor perspective** — Compliance Matrix and Preferred Tech Change are from FA; Supplier Selection is from vendor
9. **Single assessment, three documents** — all research happens during the Compliance Matrix phase; Supplier Selection and Preferred Tech Change reuse that data, not reassess
