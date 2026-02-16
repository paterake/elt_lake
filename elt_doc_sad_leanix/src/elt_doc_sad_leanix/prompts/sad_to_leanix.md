# LeanIX Integration Model Generation Prompt

This prompt is designed to enable an LLM to act as a "SAD Analyst" and generate a precise JSON blueprint for the "XML Builder" script.

## Goal
Transform an unstructured Workday SAD (System Architecture Document) into a structured JSON specification that maps to the LeanIX/diagrams.net integration model.

## Prerequisites
1.  **SAD Content**: The text content of the SAD document (extracted via python-docx).
2.  **Inventory**: A list of known applications and IT components from `config/LeanIX_Inventory.xlsx`.

## Instructions for the LLM

### 1. Context Analysis
Read the provided SAD text and identify:
*   **Integration ID**: (e.g., INT011)
*   **Source System**: The system sending data (usually Workday for outbound, or a Vendor for inbound).
*   **Target System**: The system receiving data.
*   **Intermediary**: Any middleware (e.g., SFTP, Mulesoft, AWS Lambda).
*   **Direction**: `outbound` (Workday -> Target) or `inbound` (Target -> Workday).
*   **Template Selection**: Match the integration flow to one of the **Available Templates**.
    *   *Outbound SFTP*: `integration_outbound_vendor_sftp.xml` (Workday -> SFTP -> Vendor)
    *   *Inbound SFTP*: `integration_inbound_fa_sftp.xml` (Vendor -> SFTP -> Workday)
    *   *Bidirectional*: `integration_bidirectional_api.xml`
    *   *Multi-Connector*: `integration_multi_connector.xml` (Workday <-> Gateway <-> Vendor with multiple sub-integrations)
        *   **When to use**: If the SAD describes multiple sub-integrations (e.g., INT018a, INT018b, INT018c) that share a common gateway/SFTP but have different data flows (e.g., outbound payments, inbound acknowledgements, inbound statements)
        *   **Key indicators**: Look for sub-integration IDs, multiple data flow sections, or phrases like "consists of three integrations"
*   **Process Steps**:
    *   *Extraction*: How is data pulled? (e.g., "Workday Custom Report", "RAAS", "Connector").
    *   *Security*: What encryption/auth is used? (e.g., "PGP", "SSH Keys", "OAuth").
    *   *Transmission*: Transport protocol (e.g., "SFTP", "HTTPS/REST").
    *   *Processing*: Transformation logic (e.g., "Workday Studio", "EIB", "XSLT").

### 2. Inventory Lookup (Reasoning Step)
*   Compare extracted system names against the provided **Inventory List**.
*   **Rule**: You MUST use the exact `id` and `type` from the inventory if a match exists.
*   **Heuristic**:
    *   **"Workday"** -> Choose based on integration domain:
        *   **"Workday Human Capital Management"** for: Employee identity/provisioning, HR data, travel management, demographics
        *   **"Workday Financial Management"** for: Banking/payments, credit cards, expenses, payroll settlement, pension/benefits (financial)
    *   **"SFTP"** -> Check for specific instances like "Cardinus Managed SFTP" or fallback to generic "SFTP" ITComponent.
    *   **"Interface"** -> Look for an Interface FactSheet matching the INT ID (e.g., "INT011").
    *   **"Vendor Systems"** -> Search Application type first (preferred), fallback to Provider type if no Application match.

### 3. Output Generation (JSON)
Construct a JSON object with the following schema:

#### Standard Integration Schema:
```json
{
  "title": "Workday [Target Name] Integration",
  "integration_id": "INTxxx",
  "template_id": "integration_xxxx.xml",
  "direction": "outbound|inbound|bidirectional",
  "source_system": "Name",
  "source_id": "UUID (optional)",
  "source_type": "Application|ITComponent (optional)",
  "target_system": "Name",
  "target_id": "UUID (optional)",
  "target_type": "Application|ITComponent (optional)",
  "intermediary": "Name (optional)",
  "intermediary_id": "UUID (optional)",
  "intermediary_type": "Application|ITComponent (optional)",
  "interface_id": "UUID (optional)",
  "interface_label": "Source - Target",
  "process_extraction": "Description",
  "process_security": "Description",
  "process_transmission": "Description",
  "process_processing": "Description",
  "flow_labels": [
    {
      "text": "Step 1 description",
      "x": 100, "y": 180, "width": 300, "height": 60
    }
  ],
  "security_details": ["Detail 1", "Detail 2"],
  "system_of_record": ["SoR Detail 1", "SoR Detail 2"],
  "key_attributes": ["Attribute 1", "Attribute 2"],
  "notes": ["Assumption 1", "Note 2"]
}
```

#### Multi-Connector Integration Schema:
For integrations with multiple sub-flows (e.g., INT018a, INT018b, INT018c), use:
```json
{
  "title": "Workday to [Vendor] Integration",
  "integration_id": "INTxxx",
  "template_id": "multi_connector",
  "direction": "bidirectional",
  "source_system": "Workday Financial Management",
  "source_id": "UUID from inventory",
  "source_type": "Application",
  "target_system": "Vendor Platform Name",
  "target_id": "UUID from inventory",
  "target_type": "Application",
  "intermediary": "Vendor Gateway SFTP",
  "gateway_label": "Vendor File\nGateway SFTP\nINT018",
  "intermediary_id": "UUID (if exists)",
  "intermediary_type": "Application",
  "sub_integrations": [
    {
      "title": " INT018a OUTBOUND - PAYMENT FILE GENERATION",
      "col1_header": "PAYMENT FILE GENERATION",
      "col2_header": "ENCRYPTION & TRANSMISSION",
      "col1_content": "<ul><li>Triggered: Manual launch on payroll settlement</li><li>Template: ISO 20022 V3</li><li>File Format: XML</li></ul>",
      "col2_content": "<ul><li>PGP Encryption: Using vendor public key</li><li>SFTP: SSH key authentication</li><li>Transmission: To vendor gateway</li></ul>"
    },
    {
      "title": " INT018b INBOUND - ACKNOWLEDGEMENT RETRIEVAL",
      "col1_header": "PAYMENT ACKNOWLEDGEMENT",
      "col2_header": "STATUS IMPORT",
      "col1_content": "<ul><li>Scheduled: Day after payment</li><li>File Retrieval: XML status files</li></ul>",
      "col2_content": "<ul><li>Import: Status data into Workday</li><li>Reconciliation: Payment validation</li></ul>"
    },
    {
      "title": " INT018c INBOUND - STATEMENT RETRIEVAL",
      "col1_header": "BANK STATEMENT INBOUND",
      "col2_header": "STATEMENT IMPORT",
      "col1_content": "<ul><li>Scheduled: Daily</li><li>Format: CAMT.053 XML</li></ul>",
      "col2_content": "<ul><li>Import: Bank statement data</li><li>Reconciliation: Automated</li></ul>"
    }
  ],
  "flow_labels": [
    {
      "text": "Outbound:\nINT018a: Payments Outbound\n- Manual launch\n- ISO 20022 v3 XML\n- PGP encrypted",
      "x": 560, "y": 160, "width": 370, "height": 180
    },
    {
      "text": "Inbound:\nINT018b: Acknowledgements\nINT018c: Bank Statements\n- ISO 20022 v3 XML\n- PGP encrypted",
      "x": 570, "y": 370, "width": 370, "height": 280
    }
  ],
  "security_details": ["Integration Type: Cloud Connect", "File Formats: ISO 20022 v3 XML", "Encryption: PGP"],
  "system_of_record": ["Workday: Employee and payroll data", "Vendor: Payment status and statements"],
  "key_attributes": ["Employee: Names, bank details", "Payment: Amount, date, reference"],
  "notes": ["Environment-specific keys required", "Manual launch limitation for outbound"]
}
```

## Execution
After generating the JSON, save it to a file (e.g., `spec.json`) and run:
`uv run python src/elt_doc_sad_leanix/generate_from_json.py spec.json --output-dir ~/Downloads`
