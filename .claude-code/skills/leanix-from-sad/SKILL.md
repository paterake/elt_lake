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
- Example output is at: `elt_doc_sad_leanix/examples/COR_V00_01_INT006_Barclaycard.xml`

Do NOT use the system Python directly as `python-docx` is not installed globally.

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

**5. Tables (for Lifecycle/Process sections):**
```xml
<mxCell id="[ID]" parent="1" 
        style="childLayout=tableLayout;recursiveResize=0;shadow=0;fillColor=none;verticalAlign=top;" 
        value="" vertex="1">
  <mxGeometry height="[H]" width="[W]" x="[X]" y="[Y]" as="geometry"/>
</mxCell>
```

## Color Coding Standards

| System Type | fillColor | strokeColor | Usage |
|-------------|-----------|-------------|-------|
| Workday (all modules) | #497db0 | #497db0 | Blue boxes |
| Vendors/Partners | #ffa31f | #ffa31f | Orange boxes |
| Infrastructure (Hyve) | #c17d5e | #c17d5e | Brown boxes |

## Standard Layout Positions

### Three-Box Linear Pattern (Outbound)
```
Workday HCM        →        SFTP/Vendor        →        Vendor Platform
x=240, y=280              x=560, y=280                x=880, y=280
```

### Three-Box Bi-Directional Pattern
```
Workday HCM        ↔        Vendor System        →        Downstream
x=240, y=280              x=800, y=280
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
    
    # Add source system box (Workday)
    source_id = str(id_counter)
    source_box = ET.SubElement(root_elem, 'object', {
        'type': 'factSheet',
        'label': integration_data['source_system'],
        'factSheetType': 'Application',
        'factSheetId': str(uuid.uuid4()),
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

### Template 1: Outbound EIB to SFTP
- Pattern: Workday → Vendor SFTP → Vendor Platform
- Examples: INT004 (Amex GBT), INT003 (Headspace)
- Boxes: 3 (linear)
- Arrow: Single outbound
- Sections: 4-column process breakdown

### Template 2: Bi-Directional API
- Pattern: Workday ↔ Vendor System
- Examples: INT001 (Okta)
- Boxes: 2 (Workday + Vendor)
- Arrows: Bi-directional
- Sections: Lifecycle scenarios (JML)

### Template 3: Multi-Connector Complex
- Pattern: Workday → Multiple connectors → Vendor
- Examples: INT018 (Barclays - 3 connectors)
- Boxes: Multiple for each connector
- Arrows: Various directions
- Sections: Connector-specific details

### Template 4: Via Hyve SFTP
- Pattern: Workday → Hyve SFTP → Vendor Platform
- Examples: INT002 (Crisis24)
- Boxes: 3 (with Hyve in middle)
- Arrow: Through intermediary
- Sections: Reference to INT000

## Skill Execution Steps

1. **Detect SAD upload** and diagram request
2. **Read example XML files** to understand patterns
3. **Parse SAD document** using python-docx
4. **Extract key data**:
   - Integration ID (INT###)
   - Vendor name
   - Direction (in/out/bi)
   - Security details
   - Key attributes
5. **Select template** based on integration type
6. **Generate XML** using template
7. **Add specific details**:
   - Title
   - Flow labels
   - Security box
   - System of Record
   - Key Attributes
   - Process tables (if applicable)
8. **Save XML file** with standard naming
9. **Present to user** with import instructions

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
