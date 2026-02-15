---
name: leanix-overview
description: Consolidate multiple LeanIX integration diagrams into a single overview diagram with aggregated notes sections. Use when creating or updating integration overview diagrams from existing individual integration XML files.
---

# LeanIX Integration Overview Diagram Generator

## Purpose
Consolidate multiple individual Workday integration diagrams (XML files) into a single overview diagram. The overview shows all integrations at a glance with Workday HCM as the central hub, vendor/infrastructure boxes arranged around it, and aggregated notes sections that synthesise cross-cutting themes (security, protocols, legal entities, etc.).

## Workflow

```
Individual Integration XMLs (multiple .xml files)
    ↓
Extract integration data from each XML
    ↓
Calculate layout (box positions, spacing)
    ↓
Generate consolidated diagrams.net XML
    ↓
Import directly into LeanIX ✅
```

## When to Use This Skill
- User asks to "create/generate/update the integration overview"
- User asks for a "summary diagram" or "all integrations" diagram
- User wants to consolidate multiple integration diagrams into one
- User mentions "overview" in context of LeanIX integration diagrams

**Note:** For creating individual integration diagrams from SAD documents, use the `leanix-from-sad` skill instead.

## Python Environment

This project uses a **uv workspace**. To run Python scripts for this package:

```bash
uv run --package elt-doc-leanix-overview python <script.py>
```

- The overview generator script is at: `elt_doc_leanix_overview/src/elt_doc_leanix_overview/update_overview.py`
- The verification script is at: `elt_doc_leanix_overview/src/elt_doc_leanix_overview/verify_overview.py`
- Reference XML template: `elt_doc_leanix_overview/templates/integration_overview.xml`

## Input

The user will state:
1. Whether this is a **new** overview or an **update** to an existing one
2. The **directory** containing the individual integration XML files to include
3. If updating: the **path to the existing overview XML**

The skill reads **all `.xml` files** in the supplied directory, skipping the overview file itself. Individual integration XMLs are identified by their fact sheet objects containing integration IDs (INT###).

Example prompts:
- "Create a new integration overview from the diagrams in ~/Downloads/leanix/"
- "Update the overview at ~/Downloads/Workday_Overview.xml from the integrations in ~/Downloads/leanix/"

## Output Location

- If creating new: save to the supplied directory or `~/Downloads/` with a descriptive filename (e.g. `Workday_Integration_Overview.xml`)
- If updating: overwrite the existing overview XML at its current path

## Overview Layout Structure

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

## Overview Element Specifications

**Workday HCM Box:**
- Width: 320px per integration column (minimum 1440px for 5 columns)
- Height: 250px
- Style: same as individual diagrams (blue #497db0, rounded, font 72/Helvetica Neue)
- factSheetType: Application, factSheetId from the individual XMLs

**Vendor/Infrastructure Boxes (Row 1 — directly below Workday):**
- 160×160 or 170×160, spaced 320px apart horizontally
- Apply fact sheet types and colours from the individual integration XMLs (Application=blue, Provider=orange, ITComponent=brown)
- Label format: `{Vendor Name}\n{INT###}` or `{Vendor Name}\nSFTP - {INT###}`
- If vendor not in any integration XML with a fact sheet: use plain mxCell (no fact sheet wrapper), blue fill

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

## Color Coding Standards

| System Type | fillColor | strokeColor | Usage |
|-------------|-----------|-------------|-------|
| Workday (all modules) | #497db0 | #497db0 | Blue boxes |
| Vendors/Partners | #ffa31f | #ffa31f | Orange boxes |
| Infrastructure (FA SFTP) | #d29270 | #d29270 | Brown boxes |

**Note:** Color is set via `fillColor`/`strokeColor` in the mxCell style attribute, independent of `factSheetType`.

## Overview Notes Sections

The overview notes are **aggregated summaries** across all integrations — NOT a copy-paste of individual diagram notes. Read each individual integration XML, extract the relevant details, then synthesise them into cross-cutting summary sections. See `integration_overview.xml` for the reference structure and tone.

These form the **superset** of possible sections — include all that are relevant to the integrations being summarised.

### Core Sections (Always Include)

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

### Conditional Sections (Include When Relevant)

**7. Costings Summary** — when any integration has costing data, summarise across all

**8. Environment Strategy** — when multiple environments (Sandbox/QA/Production) need documenting

**9. Critical Constraints** — when any integration has constraints, summarise across all

**10. Key Dependencies** — cross-integration dependencies (e.g. FA SFTP platform serving multiple integrations)

## Extracting Data from Individual Integration XMLs

Read each individual integration XML and extract:

1. **From `<object type="factSheet">` elements**: vendor name (label), factSheetType, factSheetId, integration ID
2. **From `<mxCell edge="1">` elements**: direction (source/target), connectivity
3. **From text labels**: flow descriptions, domain context, protocol details
4. **From info boxes** (text elements with `<h1>` or `<b>` headings): security details, system of record, key attributes, scheduling/volumes, dependencies
5. **From process tables**: workflow steps (if present)

Use this extracted data to **synthesise** the overview notes — group by theme, not by integration. Do NOT blindly concatenate individual diagram notes.

## Creating vs Updating

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

**Do NOT create intermediate Python scripts** (e.g. `generate_overview.py`) in the project. Generate the XML directly using inline Python via `uv run --package elt-doc-leanix-overview python -c "..."`. The XML output file is the only deliverable — no throwaway scripts should be left in the codebase.

## XML Structure Pattern

The XML uses mxGraph format compatible with diagrams.net and LeanIX:

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

When an Interface fact sheet exists in the individual integration XML, preserve it in the overview:

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

## Skill Execution Steps

1. **Detect overview request** — user asks to create/update integration overview
2. **Read the overview template** (`elt_doc_leanix_overview/templates/integration_overview.xml`) for structural reference
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

## Response Pattern

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

✅ **Preserve fact sheet IDs from individual XMLs** — never generate new UUIDs for systems that already have IDs
✅ **Match color codes exactly** (#497db0, #ffa31f, #d29270)
✅ **Position elements consistently** (use standard coordinates, 320px column spacing)
✅ **Synthesise notes** — aggregate by theme, not by integration
✅ **Generate unique IDs** for all new elements
✅ **Follow mxGraph structure** precisely
✅ **Preserve existing overview content** when updating (don't remove integrations)
