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
    *   *Connector*: `integration_multi_connector.xml`
*   **Process Steps**:
    *   *Extraction*: How is data pulled? (e.g., "Workday Custom Report", "RAAS", "Connector").
    *   *Security*: What encryption/auth is used? (e.g., "PGP", "SSH Keys", "OAuth").
    *   *Transmission*: Transport protocol (e.g., "SFTP", "HTTPS/REST").
    *   *Processing*: Transformation logic (e.g., "Workday Studio", "EIB", "XSLT").

### 2. Inventory Lookup (Reasoning Step)
*   Compare extracted system names against the provided **Inventory List**.
*   **Rule**: You MUST use the exact `id` and `type` from the inventory if a match exists.
*   **Heuristic**:
    *   "Workday" -> usually "Workday Human Capital Management" or "Workday Financial Management".
    *   "SFTP" -> Check for specific instances like "Cardinus Managed SFTP" or fallback to generic "SFTP" ITComponent.
    *   "Interface" -> Look for an Interface FactSheet matching the INT ID (e.g., "INT011").

### 3. Output Generation (JSON)
Construct a JSON object with the following schema:

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
    },
    {
      "text": "Step 2 description",
      "x": 450, "y": 180, "width": 300, "height": 60
    },
    {
      "text": "Step 3 description",
      "x": 800, "y": 180, "width": 300, "height": 60
    }
  ],
  "security_details": ["Detail 1", "Detail 2"],
  "notes": ["Assumption 1", "Note 2"]
}
```

## Execution
After generating the JSON, save it to a file (e.g., `spec.json`) and run:
`uv run python src/elt_doc_sad_leanix/generate_from_json.py spec.json --output-dir ~/Downloads`
