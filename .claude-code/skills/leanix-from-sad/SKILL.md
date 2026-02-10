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

## Python Environment

The Python code and dependencies for this skill live in the `elt_doc_sad_leanix` module at the project root. When running any Python code that requires `python-docx` or other dependencies, always use:

```bash
cd elt_doc_sad_leanix && uv run python <script.py>
```

- The generator script is at: `elt_doc_sad_leanix/src/elt_doc_sad_leanix/generate_integration_xml.py`
- Reference XML examples are at: `elt_doc_sad_leanix/examples/`
  - `COR_V00.01_INT001_Workday_Okta.xml` (bi-directional API)
  - `COR_V00.01_INT002_Workday_Crisis24.xml` (outbound via Hyve SFTP)
  - `COR_V00.01_INT004_AMEX_GBT.xml` (outbound to vendor SFTP)
  - `COR_V00_01_INT006_Barclaycard.xml` (inbound via Hyve SFTP)
  - `COR_V00.01_INT018_Barclays_Banking.xml` (multi-connector complex)

**Always read the closest matching reference XML before generating a new diagram.**

Do NOT use the system Python directly as `python-docx` is not installed globally.

## Output Location

Save the generated XML file in the **same directory as the input SAD `.docx` file**, with the same filename but a `.xml` extension.

For example:
- Input: `~/Downloads/SAD_INT006_Barclaycard_Visa_Credit_Card_v1_0.docx`
- Output: `~/Downloads/SAD_INT006_Barclaycard_Visa_Credit_Card_v1_0.xml`

Do NOT write output files into the project directory.

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

## Known Fact Sheet IDs

Always reuse these UUIDs for systems that already exist in LeanIX:

| System | factSheetId | factSheetType |
|--------|-------------|---------------|
| Workday Human Capital Management | `d60d172c-862d-4b73-ae8f-4205fd233d58` | Application |
| Workday Financial Management | `a1b2c3d4-e5f6-7890-abcd-ef1234567890` | Application |
| Hyve Managed SFTP Server (INT000) | `bb2e0906-47e7-4785-8a05-81e6b6c5330b` | ITComponent |

For new vendors/systems, generate a fresh UUID.

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
| Infrastructure (Hyve SFTP) | #d29270 | #d29270 | Brown boxes |

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
Vendor              →        Hyve SFTP        →        Workday
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
            - security_details: list of security items
            - key_attributes: list of attributes
            - lifecycle_scenarios: Optional dict for JML scenarios
    
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
    
    # Known fact sheet IDs (reuse for existing LeanIX systems)
    WORKDAY_HCM_FACT_SHEET_ID = 'd60d172c-862d-4b73-ae8f-4205fd233d58'
    HYVE_SFTP_FACT_SHEET_ID = 'bb2e0906-47e7-4785-8a05-81e6b6c5330b'

    # Add source system box (Workday)
    source_id = str(id_counter)
    source_box = ET.SubElement(root_elem, 'object', {
        'type': 'factSheet',
        'label': integration_data['source_system'],
        'factSheetType': 'Application',
        'factSheetId': WORKDAY_HCM_FACT_SHEET_ID,
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
    target_box = ET.SubElement(root_elem, 'object', {
        'type': 'factSheet',
        'label': target_label,
        'factSheetType': 'Provider',
        'factSheetId': str(uuid.uuid4()),
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
    
    # Add arrows based on direction
    if integration_data['direction'] in ['outbound', 'bidirectional']:
        # Outbound arrow
        outbound_arrow = ET.SubElement(root_elem, 'mxCell', {
            'id': str(id_counter),
            'edge': '1',
            'parent': '1',
            'source': source_id,
            'target': target_id,
            'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;'
        })
        geo = ET.SubElement(outbound_arrow, 'mxGeometry', {'relative': '1', 'as': 'geometry'})
        points = ET.SubElement(geo, 'Array', {'as': 'points'})
        # Add waypoints if needed
        id_counter += 1
    
    if integration_data['direction'] in ['inbound', 'bidirectional']:
        # Inbound arrow
        inbound_arrow = ET.SubElement(root_elem, 'mxCell', {
            'id': str(id_counter),
            'edge': '1',
            'parent': '1',
            'source': target_id,
            'target': source_id,
            'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;'
        })
        geo = ET.SubElement(inbound_arrow, 'mxGeometry', {'relative': '1', 'as': 'geometry'})
        points = ET.SubElement(geo, 'Array', {'as': 'points'})
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
        - security_details
        - key_attributes
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

3. **Save to file:**
```python
with open(f'COR_V00_01_{integration_data["integration_id"]}_{integration_data["integration_name"]}.xml', 'w') as f:
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

✅ Created: COR_V00_01_INT006_Barclaycard.xml

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
- Reference XML: `COR_V00.01_INT004_AMEX_GBT.xml`
- Boxes: 3 (linear), all #497db0 blue when vendor SFTP is treated as Application
- Arrow: Single outbound
- Sections: 3-4 column process breakdown (Data Extraction | File Generation | SFTP Delivery), Security, System of Record, Key Attributes

### Template 2: Outbound EIB via Hyve SFTP
- Pattern: Workday → Hyve SFTP (INT000) → Vendor Platform
- Reference XML: `COR_V00.01_INT002_Workday_Crisis24.xml`
- Boxes: 3 (Workday=#497db0, Hyve SFTP=#d29270 as ITComponent, Vendor=#497db0)
- Arrow: Single outbound through intermediary
- Sections: 4-column process breakdown (Data Extraction | Document Transformation | SFTP Delivery | Vendor Retrieval), Security, System of Record, Key Attributes

### Template 3: Bi-Directional API
- Pattern: Workday ↔ Vendor System
- Reference XML: `COR_V00.01_INT001_Workday_Okta.xml`
- Boxes: 2 (Workday=#497db0 as Application, Vendor=#ffa31f as Provider)
- Arrows: Bi-directional with waypoints routed above and below boxes
- Sections: JML lifecycle table (Joiner | Mover | Leaver | Rehire), Security, System of Record, Key Attributes

### Template 4: Inbound via Hyve SFTP
- Pattern: Vendor → Hyve SFTP → Workday
- Reference XML: `COR_V00_01_INT006_Barclaycard.xml`
- Boxes: 3 (Vendor=#ffa31f as Provider, Hyve=#d29270 as ITComponent, Workday=#497db0)
- Arrow: Single inbound
- Sections: 4-column process table (Vendor Data Generation | File Format & Encryption | SFTP Delivery | Workday Import Processing), Security, System of Record, Key Attributes, Key Dependencies

### Template 5: Multi-Connector Complex
- Pattern: Workday ↔ Vendor SFTP Gateway ↔ Vendor Platform
- Reference XML: `COR_V00.01_INT018_Barclays_Banking.xml`
- Boxes: 3 (wider spacing), bi-directional arrows
- Sub-integrations: Separate process tables per connector (e.g. INT018a, INT018b, INT018c)
- Sections: Per-connector process tables, Security, System of Record, Key Attributes, Environment Strategy, Critical Constraints

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

### Security & Technical Details
Extract from the SAD's Security, Technology Stack, and Integration Configuration sections:
- Integration Type (EIB, Cloud Connect, API)
- Template name (delivered or custom)
- File format and delimiter
- Expected volume
- Encryption: at rest (PGP) and in transit (SSH/TLS)
- Authentication method (SSH key, username/password, OAuth)
- SFTP server details
- File naming convention
- Data retention period
- Frequency and schedule
- ISU account name
- ISSG name (Integration System Security Group)
- ISSS name (Integration System Security Segment)
- Compliance certifications (SOC 2, ISO 27001, GDPR)
- Data residency

### Key Attributes Synchronized
Extract from the SAD's Data Mapping and Data Management sections. Break into sub-categories where the SAD provides detail:
- Employee/cardholder/worker identification fields
- Core data fields (names, dates, amounts, status)
- Enhanced or supplementary data categories (e.g. airline, hotel, car rental)
- Field-level detail: field name, source, format where available

### Additional Sections (include when SAD provides detail)
- **Key Dependencies**: SFTP provisioning, key exchange prerequisites, third-party dependencies, out-of-scope items
- **Environment Notes**: Sandbox/QA/Prod endpoints, environment-specific key requirements, configuration replication approach
- **Critical Constraints**: Manual launch requirements, format compliance, key regeneration on migration

## Skill Execution Steps

1. **Detect SAD upload** and diagram request
2. **Read example XML files** — always read the closest matching reference XML
3. **Parse SAD document** using python-docx
4. **Extract key data**:
   - Integration ID (INT###)
   - Vendor name
   - Direction (in/out/bi)
   - Integration type and template
   - Security details (ISU, ISSG, encryption, authentication)
   - Key attributes (with sub-categories)
   - Process workflow details (extraction, generation, delivery, monitoring)
   - Dependencies and constraints
5. **Select template** based on integration type
6. **Generate XML** using template:
   - Title
   - System boxes (fact sheets) with correct colors and UUIDs
   - Arrows with correct direction
   - Flow labels describing data movement
   - Process table with appropriate column count and content
   - Security & Technical Details box
   - System of Record box
   - Key Attributes box
   - Additional boxes (Key Dependencies, Environment Notes) when SAD provides detail
7. **Save XML file** to same directory as input SAD with `.xml` extension
8. **Present to user** with import instructions

## Critical Success Factors

✅ **Use actual UUIDs** for fact sheets
✅ **Match color codes exactly** (#497db0, #ffa31f)
✅ **Position elements consistently** (use standard coordinates)
✅ **Include proper XML escaping** for HTML content
✅ **Generate unique IDs** for all elements
✅ **Follow mxGraph structure** precisely
✅ **Test import** before delivering to user

## Next Enhancement: Full Automation

Future version could:
1. Accept SAD document path as input
2. Auto-detect integration type
3. Generate XML completely automatically
4. Validate against XSD schema
5. Preview rendering before export

But for now, this generates production-ready XML that imports perfectly into LeanIX!
