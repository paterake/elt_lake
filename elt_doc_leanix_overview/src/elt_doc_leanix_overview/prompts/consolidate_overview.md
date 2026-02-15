# LeanIX Integration Overview Consolidation Prompt

This prompt enables an LLM to act as an "Integration Analyst" and generate a JSON specification for an overview diagram that consolidates multiple individual Workday integration diagrams.

## Goal
Read multiple individual LeanIX integration XML files and produce a structured JSON specification that the "XML Builder" script can use to generate a single consolidated overview diagram.

## Prerequisites
1. **Individual Integration XMLs**: The extracted content from each `.xml` file in the source directory.
2. **Reference Template**: The structure of `integration_overview.xml` (provided as context).

## Instructions for the LLM

### 1. Extract Data from Each Integration XML

For each integration XML, identify:
* **Integration ID**: e.g. INT001, INT002, INT004, INT018, INT019
* **Vendor Name**: from the fact sheet label (e.g. "Okta", "Crisis24", "Amex GBT")
* **Fact Sheet Details**: `factSheetType`, `factSheetId`, label — for each system box
* **Direction**: outbound, inbound, or bidirectional — inferred from edge source/target
* **Protocol**: REST API, SFTP, etc. — from flow labels or info boxes
* **Frequency**: from flow labels (e.g. "Every 4 hours", "Daily", "On-demand")
* **Intermediary**: e.g. FA SFTP (INT000), Barclays File Gateway — if the integration routes through middleware
* **Downstream System**: if there's a second-hop target below the intermediary (e.g. Crisis24 below FA SFTP)
* **Domain Context**: short label like "Identity & SSO", "Travel & Expenses" — from domain labels
* **Security Details**: encryption, authentication, compliance — from info boxes
* **Volumes & Scheduling**: record counts, file sizes, frequency — from info boxes
* **Legal Entity**: which legal entity the integration serves — from info boxes

### 2. Classify Integration Layout

For each integration, determine its position in the overview:

* **Row 1 (direct)**: Integration connects Workday → Vendor directly (e.g. INT001 Okta)
* **Row 1 (intermediary)**: Integration uses middleware — the intermediary box goes in Row 1, the vendor goes in Row 2 below it (e.g. FA SFTP in Row 1, Crisis24 in Row 2)
* **Row 1 (gateway)**: Multi-connector integration — gateway in Row 1, platform in Row 2 (e.g. Barclays File Gateway in Row 1, Barclays Banking Platform in Row 2)

### 3. Synthesise Notes (Critical)

Do NOT copy-paste notes from individual diagrams. Instead, **aggregate by theme** across all integrations:

* **Data Protection**: Which integrations use PGP, SSH, both
* **Integration Protocols**: One bullet per protocol, listing which integrations use it
* **Legal Entity Segregation**: Group integrations by legal entity
* **Integration Assessment**: Classify by complexity (unidirectional, bidirectional, multi-connector)
* **Security & Compliance Framework**: Aggregate encryption, authentication, certifications, data residency, access controls, audit
* **Data Volumes & Performance**: Table with one row per integration

Include conditional sections only when relevant:
* **Costings Summary**, **Environment Strategy**, **Critical Constraints**, **Key Dependencies**

### 4. Output Generation (JSON)

Construct a JSON object with the following schema:

```json
{
  "title": "Workday Integration Overview",
  "workday": {
    "label": "Workday Human Capital Management",
    "factSheetId": "d60d172c-862d-4b73-ae8f-4205fd233d58",
    "factSheetType": "Application"
  },
  "integrations": [
    {
      "integration_id": "INT001",
      "vendor_name": "Okta",
      "factSheetId": "UUID",
      "factSheetType": "Application|Provider",
      "direction": "bidirectional",
      "protocol": "HTTPS/REST",
      "frequency": "Every 4 hours",
      "domain_label": "Identity & SSO",
      "row": 1,
      "intermediary": null,
      "downstream": null,
      "interface": {
        "factSheetId": "UUID (optional)",
        "label": "WorkDay HCM - Okta (optional)"
      }
    },
    {
      "integration_id": "INT002",
      "vendor_name": "Crisis24",
      "factSheetId": "a999052e-db90-4dfa-9d66-2e33e3ea50d8",
      "factSheetType": "Application",
      "direction": "outbound",
      "protocol": "SFTP",
      "frequency": "On-demand",
      "domain_label": "DR/BCP Employee Data",
      "row": 2,
      "intermediary": {
        "name": "FA SFTP",
        "factSheetId": "bb2e0906-47e7-4785-8a05-81e6b6c5330b",
        "factSheetType": "ITComponent",
        "integration_id": "INT000"
      },
      "downstream": null,
      "interface": {
        "factSheetId": "5c69bf97-5751-419d-83c6-1868d7f74535",
        "label": "WorkDay HCM - Crisis24"
      }
    }
  ],
  "notes": {
    "data_protection": ["All integrations use encryption (PGP and SSH)", "SSH Key authentication for SFTP connections"],
    "integration_protocols": [
      "HTTPS REST API with OAuth 2.0 (INT001)",
      "SFTP with SSH keys (INT002, INT004, INT018, INT019)"
    ],
    "legal_entity_segregation": {
      "THE FOOTBALL ASSOCIATION LIMITED": ["INT001 (Okta): All FA employees"],
      "WEMBLEY NATIONAL STADIUM LTD": ["INT001 (Okta): All WNSL employees"],
      "SHARED INFRASTRUCTURE": ["INT000 (FA SFTP): Platform service"]
    },
    "integration_assessment": {
      "single_connector_unidirectional": ["INT002 (Crisis24): EIB → CSV via SFTP"],
      "bidirectional_single_protocol": ["INT001 (Okta): Cloud Connect → REST API"],
      "multi_connector_bidirectional": ["INT018 (Barclays): 3 sub-integrations"]
    },
    "security_compliance": {
      "encryption_standards": ["Data at Rest: AES-256", "Data in Transit: TLS 1.2+, SSH, PGP"],
      "authentication_methods": ["OAuth 2.0: INT001", "SSH Key-Based: INT002, INT004"],
      "compliance_certifications": ["Workday: SOC 1/2, ISO 27001, GDPR"],
      "data_residency": ["Workday: AWS London Region"],
      "access_controls": ["Dedicated ISU per integration", "RBAC via ISSG"],
      "audit_monitoring": ["180-day retention in Workday"]
    },
    "data_volumes": [
      {"integration": "INT001", "volume": "~1,200 total workers", "target": "Every 4 hours, <5 min per sync"},
      {"integration": "INT002", "volume": "~700 active employees", "target": "<10 min end-to-end"}
    ],
    "costings_summary": null,
    "environment_strategy": null,
    "critical_constraints": null,
    "key_dependencies": null
  }
}
```

## Execution
After generating the JSON, save it to a file (e.g., `overview_spec.json`) and run:
```
uv run --package elt-doc-leanix-overview python elt_doc_leanix_overview/src/elt_doc_leanix_overview/cmd/build_xml.py overview_spec.json -o ~/Downloads/Workday_Integration_Overview.xml
```
