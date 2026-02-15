#!/usr/bin/env python3
"""
Generate Workday Integration Overview XML from a JSON Specification.
This script is the "Builder" in an LLM-driven workflow:
1. LLM reads individual integration XMLs -> Produces JSON.
2. This script reads JSON -> Produces consolidated overview XML.
"""
import sys
import json
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

# Color constants
WORKDAY_COLOR = "#497db0"
PROVIDER_COLOR = "#ffa31f"
ITCOMP_COLOR = "#d29270"
APPLICATION_COLOR = "#497db0"

COLOR_MAP = {
    "Application": APPLICATION_COLOR,
    "Provider": PROVIDER_COLOR,
    "ITComponent": ITCOMP_COLOR,
}

BOX_STYLE = (
    "shape=label;perimeter=rectanglePerimeter;fontSize=11;"
    "fontFamily=72, Helvetica Neue, Helvetica, Arial, sans-serif;"
    "align=center;verticalAlign=middle;"
    "fillColor={fill};strokeColor={fill};fontColor=#ffffff;"
    "startSize=45;whiteSpace=wrap;rounded=1;arcSize=10;html=1"
)
EDGE_STYLE = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"
TEXT_STYLE = "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;whiteSpace=wrap;overflow=hidden;rounded=0;"
NOTE_STYLE = "text;html=1;whiteSpace=wrap;overflow=hidden;rounded=0;"

# Layout constants
COLUMN_WIDTH = 320
BOX_WIDTH = 160
BOX_HEIGHT = 160
WORKDAY_HEIGHT = 250
WORKDAY_Y = 350
ROW1_Y = 960
ROW2_Y = 1320
FLOW_LABEL_Y = 800
DOMAIN_LABEL_Y = 1120
START_X = 2240


def build_overview_xml(spec):
    """Build mxGraph XML from overview JSON spec."""
    root = ET.Element('mxGraphModel', {
        'dx': '-1444', 'dy': '-350', 'grid': '0', 'gridSize': '10',
        'guides': '1', 'tooltips': '1', 'connect': '1', 'arrows': '1',
        'fold': '0', 'page': '0', 'pageScale': '1',
        'pageWidth': '826', 'pageHeight': '1169',
        'math': '0', 'shadow': '0', 'lxXmlVersion': '1',
    })

    root_elem = ET.SubElement(root, 'root')
    settings = ET.SubElement(root_elem, 'lx-settings', {'id': '0'})
    ET.SubElement(settings, 'mxCell', {'style': ''})
    ET.SubElement(root_elem, 'mxCell', {'id': '1', 'parent': '0', 'style': ''})

    id_counter = [2]  # mutable counter

    def next_id():
        val = str(id_counter[0])
        id_counter[0] += 1
        return val

    integrations = spec.get('integrations', [])

    # Determine columns: count unique Row 1 positions
    # Each integration that is direct or an intermediary occupies one column
    columns = []
    intermediary_map = {}  # intermediary_id -> column_index for downstream placement
    for integ in integrations:
        if integ.get('intermediary'):
            # Check if intermediary already has a column
            mid_id = integ['intermediary'].get('integration_id', integ['intermediary']['name'])
            if mid_id not in intermediary_map:
                intermediary_map[mid_id] = len(columns)
                columns.append(integ['intermediary'])
        else:
            columns.append(integ)

    num_columns = max(len(columns), 1)
    workday_width = COLUMN_WIDTH * num_columns

    # --- Workday HCM box ---
    wd = spec.get('workday', {})
    wd_id = next_id()
    wd_obj = ET.SubElement(root_elem, 'object', {
        'type': 'factSheet',
        'label': f"{wd.get('label', 'Workday Human Capital Management')}<div>(System of Record)</div>",
        'factSheetType': wd.get('factSheetType', 'Application'),
        'factSheetId': wd.get('factSheetId', 'd60d172c-862d-4b73-ae8f-4205fd233d58'),
        'lxCustomLabel': '1',
        'id': wd_id,
    })
    wd_cell = ET.SubElement(wd_obj, 'mxCell', {
        'parent': '1',
        'style': BOX_STYLE.format(fill=WORKDAY_COLOR),
        'vertex': '1',
    })
    ET.SubElement(wd_cell, 'mxGeometry', {
        'height': str(WORKDAY_HEIGHT), 'width': str(workday_width),
        'x': str(START_X), 'y': str(WORKDAY_Y), 'as': 'geometry',
    })

    # --- Row 1 boxes ---
    row1_ids = {}  # column_index -> element id
    col_integrations = {}  # column_index -> integration data (for flow labels)

    for col_idx, col_item in enumerate(columns):
        x = START_X + col_idx * COLUMN_WIDTH
        box_id = next_id()
        row1_ids[col_idx] = box_id

        fs_type = col_item.get('factSheetType', 'Application')
        fill = COLOR_MAP.get(fs_type, APPLICATION_COLOR)
        label = col_item.get('vendor_name', col_item.get('name', 'Unknown'))
        int_id = col_item.get('integration_id', '')
        if int_id:
            label = f"{label}<div><b>{int_id}</b></div>"

        fs_id = col_item.get('factSheetId')
        if fs_id:
            box_obj = ET.SubElement(root_elem, 'object', {
                'type': 'factSheet',
                'label': label,
                'factSheetType': fs_type,
                'factSheetId': fs_id,
                'lxCustomLabel': '1',
                'id': box_id,
            })
            box_cell = ET.SubElement(box_obj, 'mxCell', {
                'parent': '1',
                'style': BOX_STYLE.format(fill=fill),
                'vertex': '1',
            })
        else:
            box_cell = ET.SubElement(root_elem, 'mxCell', {
                'id': box_id, 'parent': '1',
                'style': BOX_STYLE.format(fill=fill),
                'value': label, 'vertex': '1',
            })
        ET.SubElement(box_cell, 'mxGeometry', {
            'height': str(BOX_HEIGHT), 'width': str(BOX_WIDTH),
            'x': str(x), 'y': str(ROW1_Y), 'as': 'geometry',
        })

    # --- Edges from Workday to Row 1 ---
    for col_idx in range(num_columns):
        box_id = row1_ids.get(col_idx)
        if not box_id:
            continue
        edge_id = next_id()
        edge = ET.SubElement(root_elem, 'mxCell', {
            'id': edge_id, 'edge': '1', 'parent': '1',
            'source': wd_id, 'target': box_id,
            'style': EDGE_STYLE,
        })
        ET.SubElement(edge, 'mxGeometry', {'relative': '1', 'as': 'geometry'})

    # --- Row 2 boxes (downstream from intermediaries) ---
    row2_ids = {}
    for integ in integrations:
        mid = integ.get('intermediary')
        if not mid:
            continue
        mid_key = mid.get('integration_id', mid['name'])
        col_idx = intermediary_map.get(mid_key)
        if col_idx is None:
            continue

        x = START_X + col_idx * COLUMN_WIDTH
        box_id = next_id()
        row2_ids[integ['integration_id']] = box_id

        fs_type = integ.get('factSheetType', 'Application')
        fill = COLOR_MAP.get(fs_type, APPLICATION_COLOR)
        label = f"{integ['vendor_name']}<div><b>{integ['integration_id']}</b></div>"

        fs_id = integ.get('factSheetId')
        if fs_id:
            box_obj = ET.SubElement(root_elem, 'object', {
                'type': 'factSheet',
                'label': label,
                'factSheetType': fs_type,
                'factSheetId': fs_id,
                'lxCustomLabel': '1',
                'id': box_id,
            })
            box_cell = ET.SubElement(box_obj, 'mxCell', {
                'parent': '1',
                'style': BOX_STYLE.format(fill=fill),
                'vertex': '1',
            })
        else:
            box_cell = ET.SubElement(root_elem, 'mxCell', {
                'id': box_id, 'parent': '1',
                'style': BOX_STYLE.format(fill=fill),
                'value': label, 'vertex': '1',
            })
        ET.SubElement(box_cell, 'mxGeometry', {
            'height': str(BOX_HEIGHT), 'width': str(BOX_WIDTH),
            'x': str(x), 'y': str(ROW2_Y), 'as': 'geometry',
        })

        # Edge from intermediary to downstream
        parent_id = row1_ids.get(col_idx)
        if parent_id:
            edge_id = next_id()
            iface = integ.get('interface')
            if iface and iface.get('factSheetId'):
                edge_obj = ET.SubElement(root_elem, 'object', {
                    'type': 'factSheet',
                    'label': iface.get('label', ''),
                    'factSheetType': 'Interface',
                    'factSheetId': iface['factSheetId'],
                    'id': edge_id,
                })
                edge_cell = ET.SubElement(edge_obj, 'mxCell', {
                    'edge': '1', 'parent': '1',
                    'source': parent_id, 'target': box_id,
                    'style': EDGE_STYLE,
                })
            else:
                edge_cell = ET.SubElement(root_elem, 'mxCell', {
                    'id': edge_id, 'edge': '1', 'parent': '1',
                    'source': parent_id, 'target': box_id,
                    'style': EDGE_STYLE,
                })
            ET.SubElement(edge_cell, 'mxGeometry', {'relative': '1', 'as': 'geometry'})

    # --- Flow labels (between Workday and Row 1) ---
    for integ in integrations:
        if integ.get('intermediary'):
            mid_key = integ['intermediary'].get('integration_id', integ['intermediary']['name'])
            col_idx = intermediary_map.get(mid_key)
        else:
            # Find column index for this direct integration
            col_idx = None
            for ci, col_item in enumerate(columns):
                if col_item.get('integration_id') == integ.get('integration_id'):
                    col_idx = ci
                    break
        if col_idx is None:
            continue

        x = START_X + col_idx * COLUMN_WIDTH
        label_parts = [integ.get('integration_id', '')]
        if integ.get('direction'):
            label_parts.append(integ['direction'].title())
        if integ.get('protocol'):
            label_parts.append(integ['protocol'])
        if integ.get('frequency'):
            label_parts.append(integ['frequency'])
        label_text = "<br>".join(label_parts)

        label_id = next_id()
        label_cell = ET.SubElement(root_elem, 'mxCell', {
            'id': label_id, 'parent': '1',
            'style': TEXT_STYLE.replace('align=left', 'align=left'),
            'value': label_text, 'vertex': '1',
        })
        ET.SubElement(label_cell, 'mxGeometry', {
            'height': '90', 'width': '190',
            'x': str(x), 'y': str(FLOW_LABEL_Y), 'as': 'geometry',
        })

    # --- Domain labels (below Row 1 boxes) ---
    for integ in integrations:
        domain = integ.get('domain_label')
        if not domain:
            continue
        if integ.get('intermediary'):
            mid_key = integ['intermediary'].get('integration_id', integ['intermediary']['name'])
            col_idx = intermediary_map.get(mid_key)
        else:
            col_idx = None
            for ci, col_item in enumerate(columns):
                if col_item.get('integration_id') == integ.get('integration_id'):
                    col_idx = ci
                    break
        if col_idx is None:
            continue

        x = START_X + col_idx * COLUMN_WIDTH
        dom_id = next_id()
        dom_cell = ET.SubElement(root_elem, 'mxCell', {
            'id': dom_id, 'parent': '1',
            'style': TEXT_STYLE,
            'value': domain, 'vertex': '1',
        })
        ET.SubElement(dom_cell, 'mxGeometry', {
            'height': '50', 'width': '130',
            'x': str(x), 'y': str(DOMAIN_LABEL_Y), 'as': 'geometry',
        })

    # --- Notes sections ---
    notes = spec.get('notes', {})
    notes_x = START_X
    notes_y = 1200
    note_width = 450
    note_gap = 40

    def add_note(title, content_html, height=160):
        nonlocal notes_y
        note_id = next_id()
        value = f'<h1 style="margin-top: 0px;"><font style="font-size: 20px;">{title}</font></h1>{content_html}'
        note_cell = ET.SubElement(root_elem, 'mxCell', {
            'id': note_id, 'parent': '1',
            'style': NOTE_STYLE,
            'value': value, 'vertex': '1',
        })
        ET.SubElement(note_cell, 'mxGeometry', {
            'height': str(height), 'width': str(note_width),
            'x': str(notes_x), 'y': str(notes_y), 'as': 'geometry',
        })
        notes_y += height + note_gap

    # Data Protection
    dp = notes.get('data_protection', [])
    if dp:
        html = "<ul>" + "".join(f"<li>{item}</li>" for item in dp) + "</ul>"
        add_note("Data Protection", html, 120)

    # Integration Protocols
    ip = notes.get('integration_protocols', [])
    if ip:
        html = "<ul>" + "".join(f"<li>{item}</li>" for item in ip) + "</ul>"
        add_note("Integration Protocols", html, 160)

    # Legal Entity Segregation
    les = notes.get('legal_entity_segregation', {})
    if les:
        html = ""
        for entity, items in les.items():
            html += f"{entity}:<ul>"
            html += "".join(f"<li>{item}</li>" for item in items)
            html += "</ul>"
        add_note("Legal Entity Segregation", html, 330)

    # Integration Assessment
    ia = notes.get('integration_assessment', {})
    if ia:
        html = ""
        labels = {
            'single_connector_unidirectional': 'Single-Connector, Unidirectional:',
            'bidirectional_single_protocol': 'Bidirectional, Single Protocol:',
            'multi_connector_bidirectional': 'Multi-Connector, Bidirectional:',
        }
        for key, label in labels.items():
            items = ia.get(key, [])
            if items:
                html += f"{label}<ul>"
                html += "".join(f"<li>{item}</li>" for item in items)
                html += "</ul>"
        if ia.get('infrastructure'):
            html += "INFRASTRUCTURE:<ul>"
            html += "".join(f"<li>{item}</li>" for item in ia['infrastructure'])
            html += "</ul>"
        add_note("INTEGRATION ASSESSMENT", html, 330)

    # Security & Compliance Framework
    sc = notes.get('security_compliance', {})
    if sc:
        html = ""
        sections = [
            ('encryption_standards', 'ENCRYPTION STANDARDS:'),
            ('authentication_methods', 'AUTHENTICATION METHODS:'),
            ('compliance_certifications', 'COMPLIANCE CERTIFICATIONS:'),
            ('data_residency', 'DATA RESIDENCY:'),
            ('access_controls', 'ACCESS CONTROLS:'),
            ('audit_monitoring', 'AUDIT & MONITORING:'),
        ]
        for key, label in sections:
            items = sc.get(key, [])
            if items:
                html += f"{label}<ul>"
                html += "".join(f"<li>{item}</li>" for item in items)
                html += "</ul>"
        add_note("SECURITY &amp; COMPLIANCE FRAMEWORK", html, 640)

    # --- Data Volumes table ---
    dv = notes.get('data_volumes', [])
    if dv:
        table_x = notes_x + note_width + 100
        table_y = 1560
        col_w = 200
        row_h = 80
        header_h = 40
        title_h = 40

        # Title
        title_id = next_id()
        title_cell = ET.SubElement(root_elem, 'mxCell', {
            'id': title_id, 'parent': '1',
            'style': 'connectable=0;recursiveResize=0;strokeColor=inherit;fillColor=none;align=center;whiteSpace=wrap;html=1;verticalAlign=middle;',
            'value': '<span style="font-size: 16px; text-wrap-mode: nowrap;">Data Volumes &amp; Performance Metrics</span>',
            'vertex': '1',
        })
        ET.SubElement(title_cell, 'mxGeometry', {
            'height': str(title_h), 'width': str(col_w * 3),
            'x': str(table_x), 'y': str(table_y), 'as': 'geometry',
        })

        # Header row
        headers = ['Integration', 'Expected Volume', 'Performance Target']
        for i, h in enumerate(headers):
            h_id = next_id()
            h_cell = ET.SubElement(root_elem, 'mxCell', {
                'id': h_id, 'parent': '1',
                'style': 'connectable=0;recursiveResize=0;strokeColor=inherit;fillColor=none;align=center;whiteSpace=wrap;html=1;verticalAlign=middle;',
                'value': f'<span style="font-size: 16px;">{h}</span>',
                'vertex': '1',
            })
            ET.SubElement(h_cell, 'mxGeometry', {
                'height': str(header_h), 'width': str(col_w),
                'x': str(table_x + i * col_w), 'y': str(table_y + title_h),
                'as': 'geometry',
            })

        # Data rows
        for row_idx, row_data in enumerate(dv):
            y = table_y + title_h + header_h + row_idx * row_h
            values = [
                f'<span style="font-size: 16px;">{row_data.get("integration", "")}</span>',
                row_data.get("volume", ""),
                row_data.get("target", ""),
            ]
            aligns = ['center', 'left', 'left']
            for col_i, (val, align) in enumerate(zip(values, aligns)):
                c_id = next_id()
                c_cell = ET.SubElement(root_elem, 'mxCell', {
                    'id': c_id, 'parent': '1',
                    'style': f'connectable=0;recursiveResize=0;strokeColor=inherit;fillColor=none;align={align};whiteSpace=wrap;html=1;verticalAlign=middle;',
                    'value': val,
                    'vertex': '1',
                })
                ET.SubElement(c_cell, 'mxGeometry', {
                    'height': str(row_h), 'width': str(col_w),
                    'x': str(table_x + col_i * col_w), 'y': str(y),
                    'as': 'geometry',
                })

    # Serialize
    return ET.tostring(root, encoding='unicode', xml_declaration=False)


def main():
    parser = argparse.ArgumentParser(description='Generate LeanIX Overview XML from JSON Specification')
    parser.add_argument('json_path', help='Path to input JSON specification file')
    parser.add_argument('-o', '--output', help='Output XML file path')
    args = parser.parse_args()

    json_path = Path(args.json_path)
    if not json_path.exists():
        print(f"Error: File {json_path} not found")
        sys.exit(1)

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            spec = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)

    required_fields = ['integrations']
    missing = [f for f in required_fields if f not in spec]
    if missing:
        print(f"Error: Missing required fields in JSON: {missing}")
        sys.exit(1)

    num_integrations = len(spec.get('integrations', []))
    print(f"Generating overview XML for {num_integrations} integrations...")

    xml = build_overview_xml(spec)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        output_path = json_path.with_suffix('.xml')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xml)

    print(f"Created: {output_path}")


if __name__ == '__main__':
    main()
