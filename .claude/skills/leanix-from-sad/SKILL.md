---
name: leanix-from-sad
description: Generate diagrams.net XML files for Workday vendor integrations from Solution Architecture Documents (SAD). Use when creating LeanIX integration diagrams, drawing architecture from SAD documents, or generating vendor integration overview diagrams.
---

# Workday Integration Diagram Generator - XML Output

## Purpose
Generate diagrams.net XML files for Workday vendor integrations that can be directly imported into LeanIX. This skill extracts information from Solution Architecture Documents (SAD), Design Documents, and email communications to produce standard

ized diagram XML files following The FA's established patterns.

## Workflow

```
SAD Document (.docx) 
    ↓
Extract key information (Python/docx)
    ↓
Generate diagrams.net XML
    ↓
Import directly into LeanIX ✅
```

**No manual recreation needed!**

## When to Use This Skill
- User uploads SAD documents and asks for diagram creation
- User says "create the diagram for this integration"
- User mentions "for LeanIX" or "draw.io"
- User references creating integration architecture diagrams
- User asks to "create/generate/update the integration overview"
- User asks for a "summary diagram" or "all integrations" diagram

## Python Environment

This project uses a **uv workspace**. The `elt_doc_sad_leanix` package and its dependencies (`python-docx`, `openpyxl`) are one workspace member. To ensure the correct dependencies are available regardless of which member was synced first, always use the `--package` flag:

```bash
uv run --package elt-doc-sad-leanix python <script.py>
```

**Why `--package`?** In a uv workspace, `uv sync` from one member (e.g. `elt_ingest_rest`) only installs that member's dependencies. A subsequent `uv sync` from another member audits but does NOT install the missing packages. The `--package` flag on `uv run` ensures the correct member's dependencies are installed before execution.

Do NOT use `cd elt_doc_sad_leanix && uv run python` — this fails when the venv was created by a different workspace member. Do NOT use the system Python directly as `python-docx` and `openpyxl` are not installed globally.

- The generator script is at: `elt_doc_sad_leanix/src/elt_doc_sad_leanix/generate_integration_xml.py`
- Reference XML templates are at: `elt_doc_sad_leanix/templates/`
  - `integration_bidirectional_api.xml` (Workday ↔ Vendor — e.g. Okta)
  - `integration_outbound_fa_sftp.xml` (Workday → FA SFTP → Vendor — e.g. Crisis24)
  - `integration_outbound_vendor_sftp.xml` (Workday → Vendor SFTP → Vendor — e.g. Amex GBT)
  - `integration_inbound_fa_sftp.xml` (Vendor → FA SFTP → Workday — e.g. Barclaycard)
  - `integration_multi_connector.xml` (Workday ↔ Gateway ↔ Vendor — e.g. Barclays Banking)
  - `integration_overview.xml` (All integrations — summary overview diagram)

**Always read the closest matching reference XML before generating a new diagram.**

## Output Location

Save the generated XML file in the **same directory as the input SAD `.docx` file**, with the same filename but a `.xml` extension.

For example:
- Input: `~/Downloads/SAD_INT006_Barclaycard_Visa_Credit_Card_v1_0.docx`
- Output: `~/Downloads/SAD_INT006_Barclaycard_Visa_Credit_Card_v1_0.xml`

Do NOT write output files into the project directory.

## Overview Diagram

### Purpose

A single diagram showing all Workday integrations at a glance. Used for ACB presentations, stakeholder briefings, and architectural documentation. Unlike individual integration diagrams (which are generated from SAD documents), the overview is generated from **existing individual integration XML files**.

### When to Generate

- User asks to **create** a new integration overview diagram
- User asks to **update** an existing integration overview diagram with additional integrations

### Input

The user will state:
1. Whether this is a **new** overview or an **update** to an existing one
2. The **directory** containing the individual integration XML files to include
3. If updating: the **path to the existing overview XML**

The skill reads **all `.xml` files** in the supplied directory, skipping the overview file itself (if it lives in the same directory). Individual integration XMLs are identified by their fact sheet objects containing integration IDs (INT###).

Example prompts:
- "Create a new integration overview from the diagrams in ~/Downloads/leanix/"
- "Update the overview at ~/Downloads/Workday_Overview.xml from the integrations in ~/Downloads/leanix/"

### Output Location

- If creating new: save to the supplied directory or `~/Downloads/` with a descriptive filename (e.g. `Workday_Integration_Overview.xml`)
- If updating: overwrite the existing overview XML at its current path

### Overview Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│              Workday Human Capital Management                   │
│                     (System of Record)                          │
│              [wide blue box: 320px per integration column]      │
└───────┬──────────┬──────────┬──────────┬──────────┬─────────────┘
        │          │          │          │          │
        ▼          ▼          ▼          ▼          ▼
   ┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌─────────┐
   │ Vendor  ││ Vendor  ││ FA SFTP ││ Vendor  ││ Gateway │
   │ INT001  ││ INT004  ││ INT000  ││ INT019  ││ INT018  │
   └─────────┘└─────────┘└────┬────┘└─────────┘└────┬────┘
                              │                      │
                              ▼                      ▼
                         ┌─────────┐            ┌─────────┐
                         │ Vendor  │            │ Vendor  │
                         │ INT002  │            │ Banking │
                         └─────────┘            └─────────┘

   [Flow labels between Workday and vendor boxes]
   [Domain context labels below vendor boxes]

   Notes Sections (left)              Data Volumes Table (right)
   ├── Data Protection                ├── Integration | Volume | Target
   ├── Integration Protocols          ├── INT001 row
   ├── Legal Entity Segregation       ├── INT002 row
   ├── Integration Assessment         └── ... per integration
   └── Security & Compliance Framework
```

### Overview Element Specifications

**Workday HCM Box:**
- Width: 320px per integration column (minimum 1440px for 5 columns)
- Height: 250px
- Style: same as individual diagrams (blue #497db0, rounded, font 72/Helvetica Neue)
- factSheetType: Application, factSheetId from LeanIX inventory

**Vendor/Infrastructure Boxes (Row 1 — directly below Workday):**
- 160×160 or 170×160, spaced 320px apart horizontally
- Apply fact sheet types and colours from LeanIX inventory (Application=blue, Provider=orange, ITComponent=brown)
- Label format: `{Vendor Name}\n{INT###}` or `{Vendor Name}\nSFTP - {INT###}`
- If vendor not in LeanIX inventory: use plain mxCell (no fact sheet wrapper), blue fill

**Downstream Boxes (Row 2 — below intermediaries like FA SFTP or Gateways):**
- Same sizing as Row 1
- Connected by edge from the intermediary box above

**Edges:**
- Style: `edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1`
- From Workday HCM box → each Row 1 box
- From intermediaries → Row 2 boxes

**Flow Labels (between Workday and Row 1 boxes):**
- Text elements positioned between the boxes (y ~800, below Workday, above vendor)
- Compact format: `INT### \n Direction \n Protocol \n Frequency`
- Width ~190px

**Domain Labels (below vendor boxes):**
- Short descriptive text: "Identity & SSO", "Travel & Expenses", "Payroll Payments", etc.
- Positioned just below each vendor box (y ~1120)

**Data Summary Label (above Workday box, right side):**
- Bullet list of key data domains: "UK Payroll & Expenses", "Employee Demographics", etc.

### Overview Notes Sections

The overview notes are **aggregated summaries** across all integrations — NOT a copy-paste of individual diagram notes. Read each individual integration XML, extract the relevant details, then synthesise them into cross-cutting summary sections. See `integration_overview.xml` for the reference structure and tone.

These form the **superset** of possible sections — include all that are relevant to the integrations being summarised.

#### Core Sections (Always Include)

**1. Data Protection**
- Summarise encryption standards used across all integrations (not per-integration — aggregate)
- Which integrations use PGP, which use SSH, which use both
- Key authentication approach summary

**2. Integration Protocols**
- One bullet per protocol/mechanism, listing which integrations use it:
  - e.g. "HTTPS REST API with OAuth 2.0 (INT001)"
  - e.g. "SFTP with SSH keys (INT002, INT004, INT018, INT019)"
  - e.g. "EIB for simple file generation (INT004, INT002)"
- Summarise Workday connector types used

**3. Legal Entity Segregation**
- Group integrations by legal entity (THE FOOTBALL ASSOCIATION LIMITED, WEMBLEY NATIONAL STADIUM LTD, SHARED INFRASTRUCTURE)
- List which integrations serve which entity, with scope notes
- Banking segregation note (when banking integrations exist)

**4. Integration Assessment**
- Classify each integration by complexity type:
  - Single-Connector, Unidirectional (e.g. EIB → SFTP)
  - Bidirectional, Single Protocol (e.g. REST API)
  - Multi-Connector, Bidirectional (e.g. 3 separate flows via gateway)
- Infrastructure services

**5. Security & Compliance Framework**
- ENCRYPTION STANDARDS: summarise at-rest, in-transit, and PGP across all integrations
- AUTHENTICATION METHODS: one bullet per method, listing which integrations use it
- COMPLIANCE CERTIFICATIONS: per vendor/platform (Workday, FA SFTP, Okta, etc.)
- DATA RESIDENCY: per platform
- ACCESS CONTROLS: ISU, ISSG, UBSG patterns (common across all integrations)
- AUDIT & MONITORING: retention periods, process monitor, archival requirements

**6. Data Volumes & Performance Metrics** (table format)
- Table with columns: Integration | Expected Volume | Performance Target
- One row per integration
- Extract volume/scheduling data from individual diagram notes

#### Conditional Sections (Include When Relevant)

**7. Costings Summary** — when any integration has costing data, summarise across all

**8. Environment Strategy** — when multiple environments (Sandbox/QA/Production) need documenting

**9. Critical Constraints** — when any integration has constraints, summarise across all

**10. Key Dependencies** — cross-integration dependencies (e.g. FA SFTP platform serving multiple integrations)

### Extracting Data from Individual Integration XMLs

Read each individual integration XML and extract:

1. **From `<object type="factSheet">` elements**: vendor name (label), factSheetType, factSheetId, integration ID
2. **From `<mxCell edge="1">` elements**: direction (source/target), connectivity
3. **From text labels**: flow descriptions, domain context, protocol details
4. **From info boxes** (text elements with `<h1>` or `<b>` headings): security details, system of record, key attributes, scheduling/volumes, dependencies
5. **From process tables**: workflow steps (if present)

Use this extracted data to **synthesise** the overview notes — group by theme, not by integration. Do NOT blindly concatenate individual diagram notes.

### Creating vs Updating

**Creating a new overview:**
1. Read all `.xml` files from the supplied directory
2. Skip any file that is the overview itself (detected by wide Workday box or user-specified output path)
3. Extract data from each individual integration XML
4. Read `integration_overview.xml` template for structural reference
5. Generate the overview XML with all integrations

**Updating an existing overview:**
1. Read the existing overview XML
2. Read all `.xml` files from the supplied directory (skip the overview file)
3. Identify which integrations already exist in the overview (by INT ID in labels)
4. Add new integrations: new boxes, new edges, extend Workday box width, add flow labels and domain labels
5. Update notes sections to include the new integration data
6. **Preserve existing content** — do NOT remove integrations that aren't in the directory

**Do NOT create intermediate Python scripts** (e.g. `generate_int006.py`) in the project. Generate the XML directly using inline Python via `uv run --package elt-doc-sad-leanix python -c "..."`. The XML output file is the only deliverable — no throwaway scripts should be left in the codebase.

## XML Structure Pattern

Based on analysis of existing LeanIX diagrams, the XML uses mxGraph format:

### Core Elements

**1. Root Structure:**
```xml
<mxGraphModel dx="240" dy="-80" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="0" page="0" pageScale="1" pageWidth="826" pageHeight="1169" math="0" shadow="0" lxXmlVersion="1">
  <root>
    <lx-settings id="0"><mxCell style=""/></lx-settings>
    <mxCell id="1" parent="0" style=""/>
    <!-- Diagram elements here -->
  </root>
</mxGraphModel>
```

**2. System Boxes (Fact Sheets):**
```xml
<object type="factSheet" label="System Name" factSheetType="Application|Provider" factSheetId="[UUID]" id="[ID]">
  <mxCell parent="1" 
          style="shape=label;perimeter=rectanglePerimeter;fontSize=11;fontFamily=72, Helvetica Neue, Helvetica, Arial, sans-serif;align=center;verticalAlign=middle;fillColor=[COLOR];strokeColor=[COLOR];fontColor=#ffffff;startSize=45;whiteSpace=wrap;rounded=1;arcSize=10;html=1" 
          vertex="1">
    <mxGeometry height="160" width="160" x="[X]" y="[Y]" as="geometry"/>
  </mxCell>
</object>
```

**3. Arrows (Edges):**
```xml
<mxCell id="[ID]" edge="1" parent="1" source="[SOURCE_ID]" target="[TARGET_ID]"
        style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;">
  <mxGeometry relative="1" as="geometry">
    <Array as="points">
      <mxPoint x="[X1]" y="[Y1]"/>
      <mxPoint x="[X2]" y="[Y2]"/>
    </Array>
  </mxGeometry>
</mxCell>
```

**3a. Interface Edges (arrows as Interface fact sheets):**

When an Interface fact sheet exists in the LeanIX inventory for this integration, wrap the edge `mxCell` in a fact sheet `object`. This links the arrow to the LeanIX Interface, making the connection visible in the LeanIX model. When no Interface exists in the inventory, use a plain `mxCell` edge (pattern 3 above).

```xml
<object type="factSheet" label="WorkDay HCM - Barclaycard"
        factSheetType="Interface"
        factSheetId="17c551bd-04b5-4397-9662-d4b78467ffae" id="[ID]">
  <mxCell edge="1" parent="1" source="[SOURCE_ID]" target="[TARGET_ID]"
          style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;">
    <mxGeometry relative="1" as="geometry"/>
  </mxCell>
</object>
```

**Note:** For multi-hop integrations (e.g. Vendor → SFTP → Workday), the Interface fact sheet goes on the primary integration edge (typically the edge connecting to Workday), not on every intermediate hop.

**4. Text Labels:**
```xml
<UserObject label="Label Text" placeholders="1" name="Variable" id="[ID]">
  <mxCell parent="1" 
          style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;overflow=hidden;fontSize=14;" 
          vertex="1">
    <mxGeometry height="[H]" width="[W]" x="[X]" y="[Y]" as="geometry"/>
  </mxCell>
</UserObject>
```

**5. Process Tables (for detailed process breakdowns):**

Process tables show the step-by-step data movement workflow beneath the diagram boxes. Column count is flexible (2-4) depending on the integration type. Use the INT002/INT004 examples as reference for standard 3-4 column tables, and INT018 for 2-column per-connector tables.

```xml
<!-- Table container -->
<mxCell id="[ID]" parent="1"
        style="childLayout=tableLayout;recursiveResize=0;shadow=0;fillColor=none;verticalAlign=top;"
        value="" vertex="1">
  <mxGeometry height="240" width="[TOTAL_WIDTH]" x="[X]" y="[Y]" as="geometry"/>
</mxCell>

<!-- Header row (child of table container) -->
<mxCell id="[ID]" parent="[TABLE_ID]"
        style="shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;top=0;left=0;bottom=0;right=0;dropTarget=0;collapsible=0;recursiveResize=0;expand=0;fontStyle=0;fillColor=none;strokeColor=inherit;"
        value="" vertex="1">
  <mxGeometry height="52" width="[TOTAL_WIDTH]" as="geometry"/>
</mxCell>

<!-- Header cells (children of header row) -->
<mxCell id="[ID]" parent="[HEADER_ROW_ID]"
        style="connectable=0;recursiveResize=0;strokeColor=inherit;fillColor=none;align=center;whiteSpace=wrap;html=1;"
        value="COLUMN HEADER" vertex="1">
  <mxGeometry height="52" width="[COL_WIDTH]" as="geometry">
    <mxRectangle height="52" width="[COL_WIDTH]" as="alternateBounds"/>
  </mxGeometry>
</mxCell>

<!-- Content row (child of table container) -->
<mxCell id="[ID]" parent="[TABLE_ID]"
        style="shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;top=0;left=0;bottom=0;right=0;dropTarget=0;collapsible=0;recursiveResize=0;expand=0;fontStyle=0;fillColor=none;strokeColor=inherit;"
        vertex="1">
  <mxGeometry height="188" width="[TOTAL_WIDTH]" y="52" as="geometry"/>
</mxCell>

<!-- Content cells (children of content row) -->
<mxCell id="[ID]" parent="[CONTENT_ROW_ID]"
        style="connectable=0;recursiveResize=0;strokeColor=inherit;fillColor=none;align=left;whiteSpace=wrap;html=1;verticalAlign=top;"
        value="<ul><li>Bullet point 1</li><li>Bullet point 2</li></ul>" vertex="1">
  <mxGeometry height="188" width="[COL_WIDTH]" as="geometry">
    <mxRectangle height="188" width="[COL_WIDTH]" as="alternateBounds"/>
  </mxGeometry>
</mxCell>
```

**Sizing notes:**
- 3-column table: total width ~890, column width ~296 each (with middle column ~298)
- 4-column table: total width ~1186, column width ~296 each
- 2-column table (INT018 style): total width ~592, column width ~296 each
- Standard heights: header row 52px, content row 188-228px
- Table y-position: typically placed below the diagram boxes and flow labels

## LeanIX Inventory Lookup

The LeanIX inventory export is at: `elt_doc_sad_leanix/config/LeanIX_Inventory.xlsx`

**Always read this inventory to resolve correct asset names and UUIDs before generating a diagram.** Do not rely on hardcoded IDs — the inventory is the source of truth.

### Inventory File Structure

- **Single sheet** named `Export ...` containing all entity types
- **Two header rows**: row 0 = machine keys (`id`, `type`, `name`, `displayName`, `description`, `level`, `status`, `lxState`), row 1 = human labels. Data starts at row 2.
- **Filter by `type` column** to find specific entity types

### Fact Sheet Types Used in Integration Diagrams

| Diagram Element | LeanIX `type` | Color | Usage |
|-----------------|---------------|-------|-------|
| Workday modules | `Application` | #497db0 (blue) | Workday HCM or Financial Management — always a box |
| Vendor systems | `Application` (preferred) or `Provider` (fallback) | #ffa31f (orange) | The vendor's software platform. Search Application first; fall back to Provider if no Application match. Color is set via `fillColor`/`strokeColor` in style, independent of factSheetType |
| Infrastructure | `ITComponent` | #d29270 (brown) | Middleware boxes (FA SFTP, Cloud Connect) |
| Integration connection | `Interface` | N/A (edge, not box) | The integration itself — applied to the arrow/edge between systems. Carries the INT ID, direction, and protocol metadata |

### Asset Resolution Process

When building a diagram from a SAD document:

1. **Read the inventory** using openpyxl (the elt_doc_sad_leanix module has it as a dependency)
2. **Identify the Workday module**: Search `type=Application` for name containing "Workday". Use the Workday Module Selection table below to pick the correct one.
3. **Identify the vendor system**: Search `type=Application` by vendor name from the SAD first. If no Application match, fall back to `type=Provider`. Use case-insensitive substring matching — SAD names may not match inventory exactly (e.g. SAD says "Barclays" but inventory has "Smartpay Fuse by Barclays").
4. **Identify infrastructure**: Search `type=ITComponent` for middleware (e.g. "SFTP").
5. **Find the Interface**: Search `type=Interface` for the integration name pattern (e.g. "WorkDay HCM - Barclaycard"). The Interface fact sheet is used on the **arrow/edge** element in the XML — wrap the edge `mxCell` in an `object` with `factSheetType="Interface"` (see Interface Edges pattern below).
6. **Use the `id` column** as the `factSheetId` in the XML. Never generate random UUIDs for systems that exist in the inventory.
7. **Use the `name` column** as the fact sheet label (with display formatting like adding `<div><b>INT006</b></div>`).

### Common Assets Reference

These are frequently used assets from the inventory. Always verify against the actual inventory file:

**Applications (boxes):**

| System | factSheetId | type | LeanIX name |
|--------|-------------|------|-------------|
| Workday HCM | `d60d172c-862d-4b73-ae8f-4205fd233d58` | Application | Workday Human Capital Management |
| Workday FM | `6f852359-0d95-43c3-b642-238be59213e7` | Application | Workday Financial Management |
| Okta | `32a7c2db-632c-46fb-88e2-f26c79a5a904` | Application | Okta |
| Amex GBT | `1ca69288-26f1-4544-8fdb-a0c798941f54` | Application | Amex GBT |
| Crisis24 | `a999052e-db90-4dfa-9d66-2e33e3ea50d8` | Application | Crisis24 |
| Headspace | `79622f37-ee3d-437f-9fc2-d1c43f7ede02` | Application | Headspace |
| Smartpay Fuse by Barclays | `6846bf4c-1405-4e76-adf5-e042b8b85f6a` | Application | Smartpay Fuse by Barclays |

**Providers (fallback for vendors without Application entries):**

| System | factSheetId | type | LeanIX name |
|--------|-------------|------|-------------|
| Barclaycard | `c400f9c3-0453-481f-b981-244f1543862b` | Provider | Barclaycard |
| American Express GBT | `ac51d761-9ab0-45de-8f34-990bce94bbe0` | Provider | American Express GBT |

**ITComponents (infrastructure boxes):**

| System | factSheetId | type | LeanIX name |
|--------|-------------|------|-------------|
| SFTP (FA SFTP) | `bb2e0906-47e7-4785-8a05-81e6b6c5330b` | ITComponent | SFTP |

**Interfaces (edges/arrows):**

| Integration | factSheetId | type | LeanIX name |
|-------------|-------------|------|-------------|
| INT001 | `33e6b2ae-ddc3-4f0d-8ff3-94339c101a82` | Interface | WorkDay HCM - OKTA |
| INT002 | `5c69bf97-5751-419d-83c6-1868d7f74535` | Interface | WorkDay HCM - Crisis24 |
| INT004 | `407149db-f671-4c4a-bbc8-73ef9680d93c` | Interface | WorkDay HCM - Amex GBT |
| INT006 | `17c551bd-04b5-4397-9662-d4b78467ffae` | Interface | WorkDay HCM - Barclaycard |
| INT003 | `12045def-269f-4ab8-8d10-ccf61c198ac9` | Interface | WorkDay HCM - Headspace |

For systems not found in the inventory, generate a fresh UUID and note it in the output so the user can create the LeanIX fact sheet.

### Workday Module Selection

The LeanIX Business Applications for Workday are **"Workday Human Capital Management"** and **"Workday Financial Management"**. Never invent module-specific names like "Workday Expenses" or "Workday Payroll" — always use one of these two:

| Integration Domain | Workday LeanIX Application |
|--------------------|---------------------------|
| Employee data, identity, provisioning, HR | Workday Human Capital Management |
| Travel management, employee demographics for vendors | Workday Human Capital Management |
| Credit card transactions, expenses | Workday Financial Management |
| Banking, payments, acknowledgements, statements | Workday Financial Management |
| Payroll settlement, payment files | Workday Financial Management |
| Pension, benefits (financial) | Workday Financial Management |

## Color Coding Standards

| System Type | fillColor | strokeColor | Usage |
|-------------|-----------|-------------|-------|
| Workday (all modules) | #497db0 | #497db0 | Blue boxes |
| Vendors/Partners | #ffa31f | #ffa31f | Orange boxes |
| Infrastructure (FA SFTP) | #d29270 | #d29270 | Brown boxes |

**Note:** Color is set via `fillColor`/`strokeColor` in the mxCell style attribute, independent of `factSheetType`. A vendor box can be `factSheetType="Application"` with orange `#ffa31f` styling — the LeanIX fact sheet type determines the data model relationship, while the color communicates the visual role in the diagram.

## Standard Layout Positions

### Two-Box Bi-Directional Pattern (e.g. INT001 Okta)
```
Workday HCM        ↔        Vendor System
x=240, y=280              x=800, y=280
```

### Three-Box Linear Pattern - Outbound via SFTP (e.g. INT002 Crisis24)
```
Workday HCM        →        SFTP (INT000)        →        Vendor Platform
x=10, y=110               x=520, y=110                x=1036, y=110
```

### Three-Box Linear Pattern - Outbound to Vendor SFTP (e.g. INT004 Amex GBT)
```
Workday HCM        →        Vendor SFTP        →        Vendor Platform
x=160, y=160              x=700, y=160              x=1190, y=160
```

### Three-Box Linear Pattern - Inbound via SFTP (e.g. INT006 Barclaycard)
```
Vendor              →        FA SFTP          →        Workday
x=240, y=280              x=560, y=280              x=880, y=280
```

### Multi-Connector Complex (e.g. INT018 Barclays Banking)
```
Workday HCM        ↔        Vendor SFTP Gateway        ↔        Vendor Platform
x=400, y=280              x=950, y=280                      x=1580, y=280
```

## Python Code Generation Template

```python
import xml.etree.ElementTree as ET
from xml.dom import minidom
import uuid

def create_integration_diagram_xml(integration_data):
    """
    Generate diagrams.net XML from integration data extracted from SAD
    
    Args:
        integration_data: dict with keys:
            - integration_id: "INT001", "INT004", etc.
            - integration_name: "Okta", "Amex GBT", etc.
            - title: Full diagram title
            - direction: "outbound", "inbound", "bidirectional"
            - source_system: "Workday Human Capital Management"
            - target_system: "Okta", "Amex GBT SFTP", etc.
            - intermediary: Optional middle system
            - flow_labels: dict of arrow labels
            - security_details: list of security items (incl. IP whitelisting, PGP details)
            - key_attributes: list of attributes
            - lifecycle_scenarios: Optional dict for JML scenarios
            - scheduling_volumes_sla: Optional list of scheduling/volume/SLA items
            - logging_monitoring: Optional list of logging/monitoring items
            - out_of_scope: Optional list of out-of-scope items
            - key_dependencies: Optional list of dependency items
            - costings: Optional list of costing/pricing items
    
    Returns:
        str: Formatted XML string
    """
    
    # Create root
    root = ET.Element('mxGraphModel', {
        'dx': '240', 'dy': '-80', 'grid': '0', 'gridSize': '10',
        'guides': '1', 'tooltips': '1', 'connect': '1', 'arrows': '1',
        'fold': '0', 'page': '0', 'pageScale': '1',
        'pageWidth': '826', 'pageHeight': '1169',
        'math': '0', 'shadow': '0', 'lxXmlVersion': '1'
    })
    
    root_elem = ET.SubElement(root, 'root')
    
    # Add settings
    settings = ET.SubElement(root_elem, 'lx-settings', {'id': '0'})
    ET.SubElement(settings, 'mxCell', {'style': ''})
    
    # Add base cell
    ET.SubElement(root_elem, 'mxCell', {'id': '1', 'parent': '0', 'style': ''})
    
    id_counter = 2
    
    # Add title
    title_cell = ET.SubElement(root_elem, 'mxCell', {
        'id': str(id_counter),
        'parent': '1',
        'style': 'text;strokeColor=none;fillColor=none;html=1;fontSize=24;fontStyle=1;verticalAlign=middle;align=center;',
        'value': integration_data['title'],
        'vertex': '1'
    })
    ET.SubElement(title_cell, 'mxGeometry', {
        'height': '40', 'width': '720', 'x': '260', 'y': '80', 'as': 'geometry'
    })
    id_counter += 1
    
    # Look up fact sheet IDs from LeanIX inventory
    # inventory_lookup is a dict returned by load_leanix_inventory() — see below
    inventory = integration_data.get('inventory_lookup', {})

    source_fs = inventory.get(integration_data['source_system'], {})
    source_fact_sheet_id = source_fs.get('id', str(uuid.uuid4()))
    source_fact_sheet_type = source_fs.get('type', 'Application')

    # Add source system box (Workday)
    source_id = str(id_counter)
    source_box = ET.SubElement(root_elem, 'object', {
        'type': 'factSheet',
        'label': integration_data['source_system'],
        'factSheetType': source_fact_sheet_type,
        'factSheetId': source_fact_sheet_id,
        'id': source_id
    })
    source_cell = ET.SubElement(source_box, 'mxCell', {
        'parent': '1',
        'style': 'shape=label;perimeter=rectanglePerimeter;fontSize=11;fontFamily=72, Helvetica Neue, Helvetica, Arial, sans-serif;align=center;verticalAlign=middle;fillColor=#497db0;strokeColor=#497db0;fontColor=#ffffff;startSize=45;whiteSpace=wrap;rounded=1;arcSize=10;html=1',
        'vertex': '1'
    })
    ET.SubElement(source_cell, 'mxGeometry', {
        'height': '160', 'width': '160', 'x': '240', 'y': '280', 'as': 'geometry'
    })
    id_counter += 1
    
    # Add target system box (Vendor)
    target_id = str(id_counter)
    target_label = f"{integration_data['target_system']}<div><b>{integration_data['integration_id']}</b></div>"
    target_fs = inventory.get(integration_data['target_system'], {})
    target_fact_sheet_id = target_fs.get('id', str(uuid.uuid4()))
    target_fact_sheet_type = target_fs.get('type', 'Provider')
    target_box = ET.SubElement(root_elem, 'object', {
        'type': 'factSheet',
        'label': target_label,
        'factSheetType': target_fact_sheet_type,
        'factSheetId': target_fact_sheet_id,
        'lxCustomLabel': '1',
        'id': target_id
    })
    target_cell = ET.SubElement(target_box, 'mxCell', {
        'parent': '1',
        'style': 'shape=label;perimeter=rectanglePerimeter;fontSize=11;fontFamily=72, Helvetica Neue, Helvetica, Arial, sans-serif;align=center;verticalAlign=middle;fillColor=#ffa31f;strokeColor=#ffa31f;fontColor=#ffffff;startSize=45;whiteSpace=wrap;rounded=1;arcSize=10;html=1',
        'vertex': '1'
    })
    
    # Position target based on pattern
    target_x = '800' if integration_data['direction'] == 'bidirectional' else '560'
    ET.SubElement(target_cell, 'mxGeometry', {
        'height': '160', 'width': '170', 'x': target_x, 'y': '280', 'as': 'geometry'
    })
    id_counter += 1
    
    # Look up Interface fact sheet for the integration edge
    interface_fs = integration_data.get('interface_fact_sheet')  # from inventory lookup

    # Helper to create an edge — wraps in Interface fact sheet if available
    def add_edge(parent_elem, edge_id, src, tgt, use_interface=True):
        edge_style = 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;'
        if use_interface and interface_fs:
            edge_obj = ET.SubElement(parent_elem, 'object', {
                'type': 'factSheet',
                'label': interface_fs['name'],
                'factSheetType': 'Interface',
                'factSheetId': interface_fs['id'],
                'id': edge_id
            })
            edge_cell = ET.SubElement(edge_obj, 'mxCell', {
                'edge': '1', 'parent': '1',
                'source': src, 'target': tgt,
                'style': edge_style
            })
        else:
            edge_cell = ET.SubElement(parent_elem, 'mxCell', {
                'id': edge_id, 'edge': '1', 'parent': '1',
                'source': src, 'target': tgt,
                'style': edge_style
            })
        geo = ET.SubElement(edge_cell, 'mxGeometry', {'relative': '1', 'as': 'geometry'})
        return edge_cell

    # Add arrows based on direction
    if integration_data['direction'] in ['outbound', 'bidirectional']:
        add_edge(root_elem, str(id_counter), source_id, target_id)
        id_counter += 1

    if integration_data['direction'] in ['inbound', 'bidirectional']:
        # For bidirectional, only first arrow gets the Interface fact sheet
        use_iface = integration_data['direction'] != 'bidirectional'
        add_edge(root_elem, str(id_counter), target_id, source_id, use_interface=use_iface)
        id_counter += 1
        id_counter += 1
    
    # Add flow labels
    for label_data in integration_data.get('flow_labels', []):
        label_obj = ET.SubElement(root_elem, 'UserObject', {
            'label': label_data['text'],
            'placeholders': '1',
            'name': 'Variable',
            'id': str(id_counter)
        })
        label_cell = ET.SubElement(label_obj, 'mxCell', {
            'parent': '1',
            'style': 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;overflow=hidden;fontSize=14;',
            'vertex': '1'
        })
        ET.SubElement(label_cell, 'mxGeometry', {
            'height': str(label_data['height']),
            'width': str(label_data['width']),
            'x': str(label_data['x']),
            'y': str(label_data['y']),
            'as': 'geometry'
        })
        id_counter += 1
    
    # Add security details box
    security_text = "<div><b>SECURITY & TECHNICAL DETAILS</b></div><div><ul>"
    for item in integration_data.get('security_details', []):
        security_text += f"<li>{item}</li>"
    security_text += "</ul></div>"
    
    security_obj = ET.SubElement(root_elem, 'UserObject', {
        'label': security_text,
        'placeholders': '1',
        'name': 'Variable',
        'id': str(id_counter)
    })
    security_cell = ET.SubElement(security_obj, 'mxCell', {
        'parent': '1',
        'style': 'text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;whiteSpace=wrap;overflow=hidden;fontSize=14;',
        'vertex': '1'
    })
    ET.SubElement(security_cell, 'mxGeometry', {
        'height': '280', 'width': '532.5', 'x': '27.5', 'y': '840', 'as': 'geometry'
    })
    id_counter += 1
    
    # Convert to string
    xml_str = ET.tostring(root, encoding='unicode')
    
    # Pretty print (optional, LeanIX doesn't care)
    dom = minidom.parseString(xml_str)
    return dom.documentElement.toxml()

# Helper function to extract data from SAD document
def extract_integration_data_from_sad(sad_path):
    """
    Extract key information from SAD document

    Returns dict with:
        - integration_id
        - integration_name
        - title
        - direction
        - source_system
        - target_system
        - flow_labels
        - security_details (incl. IP whitelisting, PGP encryption details)
        - key_attributes
        - scheduling_volumes_sla (conditional - scheduling, volumes, SLA)
        - logging_monitoring (conditional - error handling, notifications, statuses)
        - out_of_scope (conditional - items explicitly out of scope)
        - key_dependencies (conditional - prerequisites, third-party deps)
        - costings (conditional - licence fees, charges, setup costs)
    """
    from docx import Document
    
    doc = Document(sad_path)
    
    # Extract integration ID from title or content
    integration_id = None
    integration_name = None
    title = None
    
    for para in doc.paragraphs:
        text = para.text.strip()
        
        # Look for integration ID pattern: INT001, INT004, etc.
        import re
        match = re.search(r'INT\d{3,4}', text)
        if match and not integration_id:
            integration_id = match.group()
        
        # Look for title pattern
        if 'Integration' in text and 'Workday' in text:
            title = text
            
        # Extract vendor name from title
        # Pattern: "Workday Integration to [Vendor]" or "Workday to [Vendor]"
        vendor_match = re.search(r'(?:to|Integration to)\s+([A-Z][A-Za-z\s]+?)(?:\s+Integration|\s*$)', text)
        if vendor_match and not integration_name:
            integration_name = vendor_match.group(1).strip()
    
    # Determine direction from text content
    full_text = '\n'.join([p.text for p in doc.paragraphs])
    direction = 'outbound'  # default
    if 'bidirectional' in full_text.lower() or 'bi-directional' in full_text.lower():
        direction = 'bidirectional'
    elif 'inbound' in full_text.lower() and 'outbound' not in full_text.lower():
        direction = 'inbound'
    
    # Extract security details
    security_details = []
    in_security_section = False
    for para in doc.paragraphs:
        if 'Security' in para.text and ('Configuration' in para.text or 'Details' in para.text):
            in_security_section = True
            continue
        if in_security_section:
            if para.style.name.startswith('Heading'):
                in_security_section = False
            elif para.text.strip():
                # Extract bullet points or key-value pairs
                text = para.text.strip()
                if ':' in text:
                    security_details.append(text)
    
    return {
        'integration_id': integration_id or 'INTXXX',
        'integration_name': integration_name or 'Vendor',
        'title': title or f'Workday to {integration_name} Integration',
        'direction': direction,
        'source_system': 'Workday Human Capital Management',
        'target_system': integration_name or 'Vendor System',
        'flow_labels': [],  # Will be populated based on direction
        'security_details': security_details,
        'key_attributes': []
    }

def load_leanix_inventory(inventory_path):
    """
    Load the LeanIX inventory and return a lookup dict keyed by name.

    Returns dict: { 'asset name (lowercase)': {'id': uuid, 'type': factSheetType, 'name': display_name} }
    """
    import openpyxl

    wb = openpyxl.load_workbook(inventory_path, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]
    rows = list(ws.iter_rows(values_only=True))
    data = rows[2:]  # skip both header rows

    lookup = {}
    for row in data:
        asset_id, asset_type, name, display_name = row[0], row[1], row[2], row[3]
        if name and asset_type in ('Application', 'Provider', 'ITComponent', 'Interface'):
            entry = {'id': asset_id, 'type': asset_type, 'name': display_name or name}
            lookup[name.lower()] = entry
            if display_name and display_name.lower() != name.lower():
                lookup[display_name.lower()] = entry

    wb.close()
    return lookup

def resolve_asset(inventory, search_name, preferred_types=None):
    """
    Find a LeanIX asset by name with fuzzy matching.

    Args:
        inventory: dict from load_leanix_inventory()
        search_name: name to search for (from SAD)
        preferred_types: list of preferred types in priority order
            - For vendor systems: ['Application', 'Provider'] (Application preferred)
            - For infrastructure: ['ITComponent']
            - For integration edges: ['Interface']

    Returns: {'id': uuid, 'type': type, 'name': name} or None
    """
    search = search_name.lower().strip()

    # Exact match
    if search in inventory:
        match = inventory[search]
        if not preferred_types or match['type'] in preferred_types:
            return match

    # Substring match — prefer matches in preferred_types order
    candidates = []
    for key, entry in inventory.items():
        if search in key or key in search:
            candidates.append(entry)

    if preferred_types:
        for ptype in preferred_types:
            for c in candidates:
                if c['type'] == ptype:
                    return c

    return candidates[0] if candidates else None
```

## Usage Example

When user uploads SAD document:

1. **Parse the SAD:**
```python
integration_data = extract_integration_data_from_sad('/path/to/SAD_INT006.docx')
```

2. **Generate XML:**
```python
xml_content = create_integration_diagram_xml(integration_data)
```

3. **Save to file** (same directory as input SAD, same filename with `.xml` extension):
```python
output_path = sad_path.with_suffix('.xml')
with open(output_path, 'w') as f:
    f.write(xml_content)
```

4. **User imports into LeanIX!**

## Standard Response Pattern

When user uploads SAD and asks for diagram:

```
I'll create the diagrams.net XML file for this integration.

[Parse SAD document]
[Extract key information]
[Generate XML using template]
[Save XML file]

✅ Created: SAD_INT006_Barclaycard_Visa_Credit_Card_v1_0.xml

You can now:
1. Download this XML file
2. In LeanIX, create a new diagram
3. Import this XML file
4. The diagram will appear fully formatted!

Would you like me to adjust any positions, colors, or add more details?
```

## Advantages Over Text Approach

| Aspect | Text Descriptions | XML Generation ✅ |
|--------|------------------|-------------------|
| **Manual Work** | Must recreate in LeanIX | Direct import |
| **Consistency** | Manual errors possible | Perfect consistency |
| **Speed** | 30-60 minutes | 30 seconds |
| **Formatting** | Manual positioning | Auto-positioned |
| **Updates** | Recreate everything | Regenerate XML |
| **Color Coding** | Manual selection | Automatic |
| **UUIDs** | Manual generation | Auto-generated |

## Integration Type Templates

### Template 1: Outbound EIB to Vendor SFTP
- Pattern: Workday → Vendor SFTP → Vendor Platform
- Reference XML: `integration_outbound_vendor_sftp.xml`
- Boxes: 3 (Workday=Application blue, Vendor SFTP=Application orange, Vendor Platform=Application orange)
- Arrows: Single outbound; primary arrow uses Interface fact sheet
- Core sections: Process table (3-4 columns), Security & Technical Details, System of Record, Key Attributes
- Conditional sections: Scheduling/Volumes/SLA, Logging & Monitoring, Out of Scope, Key Dependencies, Costings, Environment Notes

### Template 2: Outbound EIB via FA SFTP
- Pattern: Workday → FA SFTP (INT000) → Vendor Platform
- Reference XML: `integration_outbound_fa_sftp.xml`
- Boxes: 3 (Workday=Application blue, FA SFTP=ITComponent brown, Vendor=Application orange)
- Arrows: Single outbound through intermediary; Interface fact sheet on primary edge
- Core sections: Process table (4 columns), Security & Technical Details, System of Record, Key Attributes
- Conditional sections: Scheduling/Volumes/SLA, Logging & Monitoring, Out of Scope, Key Dependencies, Costings

### Template 3: Bi-Directional API
- Pattern: Workday ↔ Vendor System
- Reference XML: `integration_bidirectional_api.xml`
- Boxes: 2 (Workday=Application blue, Vendor=Application orange or Provider orange if no Application)
- Arrows: Bi-directional with waypoints; one arrow uses Interface fact sheet
- Core sections: JML lifecycle table (Joiner | Mover | Leaver | Rehire), Security & Technical Details, System of Record, Key Attributes
- Conditional sections: Scheduling/Volumes/SLA, Logging & Monitoring, Out of Scope, Costings

### Template 4: Inbound via FA SFTP
- Pattern: Vendor → FA SFTP → Workday
- Reference XML: `integration_inbound_fa_sftp.xml`
- Boxes: 3 (Vendor=Provider orange or Application orange, FA SFTP=ITComponent brown, Workday=Application blue)
- Arrows: Single inbound; Interface fact sheet on edge connecting to Workday
- Core sections: Process table (4 columns), Security & Technical Details, System of Record, Key Attributes
- Conditional sections: Scheduling/Volumes/SLA, Logging & Monitoring, Out of Scope, Key Dependencies, Costings

### Template 5: Multi-Connector Complex
- Pattern: Workday ↔ Vendor SFTP Gateway ↔ Vendor Platform
- Reference XML: `integration_multi_connector.xml`
- Boxes: 3 (Workday=Application blue, Gateway=Application orange, Platform=Application orange)
- Arrows: Bi-directional; Interface fact sheets per sub-integration where available
- Sub-integrations: Separate process tables per connector (e.g. INT018a, INT018b, INT018c)
- Core sections: Per-connector process tables, Security & Technical Details, System of Record, Key Attributes
- Conditional sections: Scheduling/Volumes/SLA, Logging & Monitoring, Out of Scope, Costings, Environment Notes, Critical Constraints

## Process Table Content Guidance

Every integration diagram should include a process table below the boxes and flow labels. The number of columns (2-4) depends on the integration type. Extract content from the SAD document to populate each column.

### Standard Columns

| Column | Outbound (Workday sends) | Inbound (Vendor sends) |
|--------|--------------------------|------------------------|
| **Data Extraction / Source** | EIB/report name, custom report details, data scope/filters, expected volume, full file vs delta, worker types included/excluded | Vendor source system, file types (starter/daily), delivery schedule, data scope, expected volume |
| **File Generation / Format** | Output format (CSV, XML, pipe-delimited), delimiter, character encoding (UTF-8), file naming convention, header rows, document transformation | File format specification (e.g. VCF4.4), delimiter (tab/pipe/comma), character encoding, file naming convention, file size |
| **Data Delivery / Transport** | PGP encryption (whose key), SFTP endpoints (QA + Prod), destination directory, SSH key authentication, IP whitelisting, file retention/purge policy | PGP encryption at rest (mandatory/optional), SFTP server details, SSH authentication, file retrieval method (push vs pull), file retention |
| **Processing / Monitoring** | Integration event logging in Process Monitor, output file attachment, status tracking (Completed/Warnings/Errors/Failed), notification rules, error thresholds | Import template name, file validation, data integrity checks, orphaned record handling, status tracking, notification rules, error handling |

### Column Count Guidelines

- **2 columns**: Use for sub-integrations within a multi-connector (e.g. INT018a, INT018b) where each sub-integration is simpler
- **3 columns**: Use when extraction and generation are combined, or when monitoring is minimal
- **4 columns**: Use for standard single-connector integrations — most common pattern

## Information Box Content Guidance

Every diagram includes three core note sections (always present) plus conditional sections included when the SAD provides relevant detail.

### Core Sections (always present)

#### 1. Security & Technical Details
Extract from the SAD's Security, Technology Stack, and Integration Configuration sections. Focus on security and technical configuration — scheduling and volume details belong in the Scheduling, Volumes & SLA section.
- Integration Type (EIB, Cloud Connect, API)
- Template name (delivered or custom)
- File format and delimiter
- Encryption at rest: PGP encryption details — mandatory/optional, whose key, environment-specific keys (Sandbox, Implementation, Production)
- Encryption in transit: SSH/TLS for SFTP connections
- Authentication method (SSH key, username/password, OAuth)
- IP whitelisting: vendor delivery IPs, Workday retrieval IPs, environment-specific requirements
- SFTP server details (host, directories, environment-specific endpoints)
- File naming convention
- Data retention period
- ISU account name
- ISSG name (Integration System Security Group)
- ISSS name (Integration System Security Segment)
- Compliance certifications (SOC 2, ISO 27001, GDPR)
- Data residency

#### 2. System of Record
- Which system is the authoritative source for the data
- Which system is the target/consumer
- Scope (e.g. "FA employees only", "contractors excluded")

#### 3. Key Attributes Synchronized
Extract from the SAD's Data Mapping and Data Management sections. Break into sub-categories where the SAD provides detail:
- Employee/cardholder/worker identification fields
- Core data fields (names, dates, amounts, status)
- Enhanced or supplementary data categories (e.g. airline, hotel, car rental)
- Field-level detail: field name, source, format where available

### Conditional Sections (include when SAD provides detail)

#### 4. Scheduling, Volumes & SLA
Include this section when the SAD provides detail on scheduling, data volumes, or performance targets. Combines three related operational concerns into one section. Extract from the SAD's Integration Configuration, Functionality, and any SLA/Performance sections.
- **Scheduling**: Frequency (daily, hourly, on-demand), automation approach (Cloud Connect scheduled, EIB, API polling), schedule owner (e.g. "FA finance team"), manual launch capability and who can trigger it
- **Volumetrics**: Expected data volumes (record counts, file sizes), full file vs delta, number of file types (starter file, daily transaction file), growth expectations
- **SLA / Performance Targets**: Only if the SAD specifies them — processing time requirements, delivery windows, uptime commitments

#### 5. Logging & Monitoring
Include this section when the SAD provides detail on error handling, monitoring, or notification processes. Extract from Error Handling, Maintenance, and Support sections.
- Error handling approach: validation steps, error thresholds (e.g. "up to 500 errors before processing stops")
- Integration event statuses: list the possible statuses (Completed, Completed with Warnings, Completed with Errors, Failed)
- Notification rules: who receives notifications, on what events (warnings, errors, failures only vs always)
- Process Monitor: how operational teams monitor integration health
- Orphaned record handling or other data quality processes
- First-line troubleshooting: which team handles what category of issue

#### 6. Out of Scope
Include this section when the SAD explicitly identifies items as out of scope or not covered by this integration. Extract from Constraints, Dependencies, and Functionality sections.
- Downstream processes not covered (e.g. "journal posting to Great Plains")
- Excluded populations (e.g. "contractors", "terminated employees")
- Related but separate integrations
- Features deferred to future phases
- Items requiring separate solutions

#### 7. Key Dependencies
Prerequisites and third-party dependencies required for the integration to function. Extract from Dependencies and Constraints sections. **Note:** Out-of-scope items should go in the Out of Scope section, not here.
- SFTP provisioning requirements
- Key exchange prerequisites (PGP, SSH)
- Third-party dependencies (vendor configuration, test environment access)
- Internal dependencies (Workday configuration, worker data setup)

#### 8. Costings
Include this section when the SAD includes licensing, pricing, or cost information. Extract from any Costings, Pricing, Licensing, or Commercial sections.
- Licence or subscription fees (vendor platform, SFTP hosting, middleware)
- Per-transaction or volume-based charges
- One-off implementation or setup costs
- Ongoing support or maintenance costs
- Cost allocation (which team/budget bears the cost)

#### 9. Environment Notes
Sandbox/QA/Prod endpoints, environment-specific key requirements, configuration replication approach.

#### 10. Critical Constraints
Manual launch requirements, format compliance, key regeneration on migration, hypercare limitations.

## Skill Execution Steps

1. **Detect SAD upload** and diagram request
2. **Read the LeanIX inventory** (`elt_doc_sad_leanix/config/LeanIX_Inventory.xlsx`) using openpyxl to build an asset lookup
3. **Read example XML files** — always read the closest matching reference XML
4. **Parse SAD document** using python-docx
5. **Extract key data**:
   - Integration ID (INT###)
   - Vendor name
   - Direction (in/out/bi)
   - Integration type and template
   - Security details (ISU, ISSG, encryption, authentication, IP whitelisting, PGP key details)
   - Key attributes (with sub-categories)
   - Process workflow details (extraction, generation, delivery, monitoring)
   - Scheduling details (frequency, automation approach, schedule owner, manual launch)
   - Volumetrics (expected volumes, file sizes, record counts, full vs delta)
   - Logging & monitoring (error handling, thresholds, notifications, statuses)
   - Out-of-scope items (explicitly stated exclusions, deferred items)
   - Dependencies and constraints
   - SLA / performance targets (if specified)
   - Costings (licence fees, per-transaction charges, setup costs — if specified)
6. **Resolve LeanIX assets** — look up each system in the inventory:
   - Match the Workday module (HCM or Financial Management) by integration domain
   - Match the vendor by name (check Provider, then Application)
   - Match infrastructure components (ITComponent)
   - Use inventory `id` values as `factSheetId` in the XML
   - Flag any systems not found in the inventory
7. **Select template** based on integration type
8. **Generate XML** using template:
   - Title
   - System boxes (fact sheets) with correct colors, types, and inventory UUIDs
   - Arrows with correct direction
   - Flow labels describing data movement
   - Process table with appropriate column count and content
   - **Core note sections (always):**
     - Security & Technical Details box (with IP whitelisting, PGP encryption details)
     - System of Record box
     - Key Attributes box
   - **Conditional note sections (when SAD provides detail):**
     - Scheduling, Volumes & SLA box
     - Logging & Monitoring box
     - Out of Scope box
     - Key Dependencies box
     - Costings box
     - Environment Notes box
     - Critical Constraints box
9. **Save XML file** to same directory as input SAD with `.xml` extension
10. **Present to user** with import instructions and list any systems that were not found in the inventory

### For Integration Overview Diagram

1. **Detect overview request** — user asks to create/update integration overview
2. **Read the overview template** (`elt_doc_sad_leanix/templates/integration_overview.xml`) for structural reference
3. **Read all `.xml` files** from the supplied directory (skip the overview file itself)
4. **If updating**: read the existing overview XML to preserve current content
5. **Extract per-integration data** from each individual XML:
   - Integration ID, vendor name, direction, fact sheet details
   - Security details, protocols, authentication
   - Volumes, SLA, scheduling
   - System of record, key attributes
   - Legal entity scope
   - Dependencies, constraints, costings (if present)
6. **Generate layout**:
   - Calculate Workday box width (320px × number of integration columns)
   - Position vendor boxes in Row 1 (320px spacing, starting x=2240)
   - Position downstream boxes in Row 2 where intermediaries exist (y offset +360)
   - Create edges from Workday to Row 1 boxes, and from intermediaries to Row 2
   - Add flow labels between boxes and domain labels below vendor boxes
7. **Generate notes sections** using the overview superset, populating from extracted data
8. **If updating**: merge new integrations with existing, preserving current content
9. **Save XML** to user-specified path
10. **Present to user** with summary table of integrations included

### Overview Response Pattern

```
✅ Created/Updated: {filename}

**Integrations included ({count}):**
| INT ID | Vendor | Direction | Type |
|--------|--------|-----------|------|
| INT001 | Okta   | Bi-directional | API |
| ...    | ...    | ...       | ...  |

You can now:
1. Download this XML file
2. In LeanIX, create a new diagram (or replace existing)
3. Import this XML file
4. The overview diagram will appear fully formatted!
```

## Critical Success Factors

✅ **Look up UUIDs from LeanIX inventory** — never use placeholder or random UUIDs for known systems
✅ **Match color codes exactly** (#497db0, #ffa31f, #d29270)
✅ **Position elements consistently** (use standard coordinates)
✅ **Include proper XML escaping** for HTML content
✅ **Generate unique IDs** for all elements
✅ **Follow mxGraph structure** precisely
✅ **Flag missing assets** — tell user if a system from the SAD was not found in the inventory

## Next Enhancement: Full Automation

Future version could:
1. Accept SAD document path as input
2. Auto-detect integration type
3. Generate XML completely automatically
4. Validate against XSD schema
5. Preview rendering before export

But for now, this generates production-ready XML that imports perfectly into LeanIX!
