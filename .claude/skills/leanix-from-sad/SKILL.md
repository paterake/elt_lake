---
name: leanix-from-sad
description: Generate diagrams.net XML files for individual Workday vendor integrations from Solution Architecture Documents (SAD). Use when creating LeanIX integration diagrams or drawing architecture from SAD documents.
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
- For overview/consolidation diagrams, use the `leanix-overview` skill instead

## Python Environment

This project uses a **uv workspace**. The `elt_doc_sad_leanix` package and its dependencies (`python-docx`, `openpyxl`) are one workspace member. To ensure the correct dependencies are available regardless of which member was synced first, always use the `--package` flag:

```bash
uv run --package elt-doc-sad-leanix python <script.py>
```

**Why `--package`?** In a uv workspace, `uv sync` from one member (e.g. `elt_ingest_rest`) only installs that member's dependencies. A subsequent `uv sync` from another member audits but does NOT install the missing packages. The `--package` flag on `uv run` ensures the correct member's dependencies are installed before execution.

Do NOT use `cd elt_doc_sad_leanix && uv run python` — this fails when the venv was created by a different workspace member. Do NOT use the system Python directly as `python-docx` and `openpyxl` are not installed globally.

- The generator class is at: `elt_doc_sad_leanix/src/elt_doc_sad_leanix/diagram_generator.py`
- The JSON→XML CLI builder: `elt_doc_sad_leanix/src/elt_doc_sad_leanix/cmd/build_xml.py`
- The LLM prompt compiler: `elt_doc_sad_leanix/src/elt_doc_sad_leanix/cmd/compile_context.py`
- The LLM prompt template: `elt_doc_sad_leanix/src/elt_doc_sad_leanix/prompts/sad_to_leanix.md`
- Legacy heuristic parser: `elt_doc_sad_leanix/src/elt_doc_sad_leanix/legacy/generate_from_sad.py`
- Reference XML templates are at: `elt_doc_sad_leanix/templates/`
  - `integration_bidirectional_api.xml` (Workday ↔ Vendor — e.g. Okta)
  - `integration_outbound_fa_sftp.xml` (Workday → FA SFTP → Vendor — e.g. Crisis24)
  - `integration_outbound_vendor_sftp.xml` (Workday → Vendor SFTP → Vendor — e.g. Amex GBT)
  - `integration_inbound_fa_sftp.xml` (Vendor → FA SFTP → Workday — e.g. Barclaycard)
  - `integration_multi_connector.xml` (Workday ↔ Gateway ↔ Vendor — e.g. Barclays Banking)

**Always read the closest matching reference XML before generating a new diagram.**

## Output Location

Save the generated XML file in the **same directory as the input SAD `.docx` file**, with the same filename but a `.xml` extension.

For example:
- Input: `~/Downloads/SAD_INT006_Barclaycard_Visa_Credit_Card_v1_0.docx`
- Output: `~/Downloads/SAD_INT006_Barclaycard_Visa_Credit_Card_v1_0.xml`

Do NOT write output files into the project directory.

**Note:** For overview/consolidation diagrams (combining multiple integration XMLs into one), use the `leanix-overview` skill instead.

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
8. **For multi-connector integrations**: ALL 3 boxes must be wrapped as fact sheet objects with inventory UUIDs:
   - Workday box: Use the appropriate Workday Application UUID (HCM or FM based on integration domain)
   - Gateway box: Use the vendor's Application UUID from inventory (search by vendor name)
   - Platform box: Use the same vendor Application UUID (both vendor boxes typically reference the same inventory asset)
   - The diagram generator will automatically create fact sheet objects when `source_id`, `intermediary_id`, and `target_id` are provided in the spec

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

## Code Reference

For XML generation patterns, read:
- `diagram_generator.py` — the `WorkdayIntegrationDiagramGenerator` class with `add_system_box()`, `add_edge()`, `add_info_box()`, and `generate_xml()` methods
- `legacy/generate_from_sad.py` — heuristic SAD parsing and XML generation
- Reference XML templates in `elt_doc_sad_leanix/templates/` — always read the closest matching template before generating

The generator uses `xml.etree.ElementTree` to build mxGraph XML. When setting HTML content as attribute values (e.g. `<div><b>INT006</b></div>`), pass raw HTML — ET handles the escaping automatically. Pre-escaping causes double-escaping.

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
- **CRITICAL**: All 3 boxes MUST be wrapped as fact sheet objects with inventory UUIDs:
  - Workday box: Use Workday FM/HCM Application UUID
  - Gateway box: Use vendor Application UUID (e.g., Smartpay Fuse by Barclays)
  - Platform box: Use same vendor Application UUID (both Barclays boxes share the same UUID)
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

## Critical Success Factors

✅ **Look up UUIDs from LeanIX inventory** — never use placeholder or random UUIDs for known systems
✅ **Match color codes exactly** (#497db0, #ffa31f, #d29270)
✅ **Position elements consistently** (use standard coordinates)
✅ **Include proper XML escaping** for HTML content
✅ **Generate unique IDs** for all elements
✅ **Follow mxGraph structure** precisely
✅ **Flag missing assets** — tell user if a system from the SAD was not found in the inventory
