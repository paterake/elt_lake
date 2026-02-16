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
    *   **"Workday"** -> **IMPORTANT: First check if the SAD explicitly mentions "Workday HCM" or "Workday FM" / "Workday Financial Management" / "Workday Financials" in the System of Record, Source Systems, or Overview sections. If it does, use that module.** Only if the SAD does not explicitly mention a module, choose based on integration domain:
        *   **"Workday Human Capital Management"** for: Employee identity/provisioning, HR data, travel management, demographics
        *   **"Workday Financial Management"** for: Banking/payments, credit cards, expenses, payroll settlement, pension/benefits (financial)
    *   **"SFTP"** -> Check for specific instances like "Cardinus Managed SFTP" or fallback to generic "SFTP" ITComponent.
    *   **"Interface"** -> Look for an Interface FactSheet matching the INT ID (e.g., "INT011").
    *   **"Vendor Systems"** -> Search Application type first (preferred), fallback to Provider type if no Application match.

### 3. Content Extraction from SAD
Extract detailed information from specific SAD sections:

*   **Security Details**: Extract from "Security", "Technology Stack", "Integration Configuration" sections:
    - Integration type (EIB, Cloud Connect, API)
    - File formats and delimiters
    - Encryption details (PGP keys, SSH keys, environment-specific)
    - Authentication methods
    - IP whitelisting requirements
    - Data retention periods
    - Compliance certifications

*   **System of Record**: Extract from "Data Sources", "System of Record" sections:
    - Which systems are authoritative for which data
    - Data scope (legal entities, populations included/excluded)

*   **Key Attributes**: Extract from "Data Mapping", "Data Management" sections:
    - Group by data flow direction (OUTBOUND, INBOUND)
    - List specific fields being synchronized
    - Use nested HTML lists with bold subheadings for organization

*   **Environment Notes**: Extract from "Environments", "DevOps", "Deployment" sections:
    - Environment strategy (Sandbox, Implementation, Production)
    - Environment-specific configurations
    - Key exchange procedures
    - Contact information for vendors

*   **Critical Constraints**: Extract from "Constraints", "Dependencies", "Out of Scope" sections:
    - Manual processes required
    - Technical limitations
    - Compliance requirements
    - Scope restrictions

### 4. Output Generation (JSON)
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
  "security_details": ["Detail 1", "Detail 2", "..."],
  "system_of_record": ["SoR Detail 1", "SoR Detail 2", "..."],
  "key_attributes": [
    "<b>Category 1:</b>",
    "<ul><li>Field 1: Description</li><li>Field 2: Description</li></ul>",
    "<b>Category 2:</b>",
    "<ul><li>Field 3: Description</li></ul>"
  ],
  "environment_notes": ["Environment detail 1", "..."],
  "critical_constraints": ["Constraint 1", "..."],
  "notes": ["Additional note 1", "..."]
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
  "security_details": [
    "Integration Type: Workday Cloud Connect (3 integrations)",
    "File Formats: ISO 20022 v3 XML (payments & acknowledgements), CAMT.053 XML (statements)",
    "Expected Volumes: ~2,000-2,500 monthly payments across all runs",
    "Encryption: PGP encryption using Barclays public key (outbound) & Workday public key (inbound)",
    "Authentication: SSH key-based SFTP (environment-specific keys required)",
    "Data in Transit: SSH encryption layer on SFTP connections",
    "Document Retention: Integration output files stored 180 days in Workday",
    "File Validation: Barclays MyStandards portal for ISO 20022 v3 BACS format compliance",
    "Environment Isolation: Separate SSH/PGP keys for Sandbox, Implementation, Production"
  ],
  "system_of_record": [
    "Workday HCM: Employee records, organizational data, bank account details",
    "Workday Payroll: UK payroll settlement data (gross pay, deductions, net pay, payment dates)",
    "Workday Expenses: Expense claim settlement data (amounts, claimants, payment dates)",
    "Workday Banking: Target for payment status acknowledgements and bank statement imports",
    "Scope: The Football Association Limited only; BACS payments only"
  ],
  "key_attributes": [
    "<b>OUTBOUND (Payments):</b>",
    "<ul><li>Employee/Claimant: Legal names, bank account number, sort code</li><li>Payment Details: Net pay/reimbursement amount, payment date, reference</li><li>Organizational: Legal entity (The FA Limited), cost center, payment type</li></ul>",
    "<b>INBOUND (Acknowledgements):</b>",
    "<ul><li>Payment Status: Processed, Failed, Pending</li><li>Bank Reference: Barclays transaction references</li><li>Status Dates: Processing date, confirmation timestamp</li></ul>",
    "<b>INBOUND (Statements):</b>",
    "<ul><li>Account Balance: Opening balance, closing balance, available funds</li><li>Transactions: Debits, credits, transaction dates, references</li><li>Account: Barclays *****220 (The FA Limited)</li></ul>"
  ],
  "environment_notes": [
    "Sandbox: Integration development, initial testing, key validation",
    "Implementation (Preview): UAT, end-to-end testing with Barclays test environment",
    "Production (Gold): Live payment processing from April 1, 2026",
    "Environment-Specific Configuration:",
    "<ul><li>Unique SSH keys per environment (regenerated on tenant migration)</li><li>Unique PGP key pairs per environment</li><li>Separate SFTP endpoints registered with Barclays Integration Manager</li></ul>",
    "Key Exchange: Keys provided to Barclays contacts (matthew.gregory@barclays.com, <br/>  simon.tyrrell@barclays.com, michael.umoh@barclays.com)"
  ],
  "critical_constraints": [
    "Manual Launch Required: INT018a cannot be scheduled automatically - must be <br/>  manually launched on settlement completion (Workday parameter limitation)",
    "Banking Standards: Payment files must pass Barclays MyStandards portal validation",
    "Environment-Specific Keys: SSH and PGP keys must be regenerated and registered <br/>  with Barclays for each environment migration",
    "Hypercare Limitation: All issues must be identified within hypercare period per SOW",
    "Payment Types: BACS only - no Faster Payments or CHAPS",
    "Legal Entity: The Football Association Limited only (Account *****220)"
  ]
}
```

## Execution
After generating the JSON, save it to a file (e.g., `spec.json`) and run:
`uv run python src/elt_doc_sad_leanix/generate_from_json.py spec.json --output-dir ~/Downloads`
