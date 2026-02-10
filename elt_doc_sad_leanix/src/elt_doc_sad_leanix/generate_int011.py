#!/usr/bin/env python3
"""
Generate LeanIX diagrams.net XML for INT011 Cardinus Employee Demographic Outbound
Extracted from SAD: SAD_INT011_Cardinus_V1_0.docx
Pattern: Outbound via direct SFTP (Workday HCM → Cardinus)
"""

import xml.etree.ElementTree as ET
import sys


def generate_int011_xml(output_path: str):
    """Generate the INT011 Cardinus diagram XML."""

    # --- LeanIX inventory assets ---
    WORKDAY_HCM = {
        "id": "d60d172c-862d-4b73-ae8f-4205fd233d58",
        "type": "Application",
        "name": "Workday Human Capital Management",
    }
    CARDINUS = {
        "id": "ce3f0dd9-3e4f-4720-a2be-a11de220d1fd",
        "type": "Application",
        "name": "Cardinus",
    }
    INTERFACE_INT011 = {
        "id": "3597f160-5605-4712-a6dd-36ff6b12a492",
        "type": "Interface",
        "name": "WorkDay HCM - Cardinus",
    }

    # --- Colours ---
    BLUE = "#497db0"
    ORANGE = "#ffa31f"

    BOX_STYLE = (
        "shape=label;perimeter=rectanglePerimeter;fontSize=11;"
        "fontFamily=72, Helvetica Neue, Helvetica, Arial, sans-serif;"
        "align=center;verticalAlign=middle;"
        "fillColor={color};strokeColor={color};fontColor=#ffffff;"
        "startSize=45;whiteSpace=wrap;rounded=1;arcSize=10;html=1"
    )
    EDGE_STYLE = (
        "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;"
        "jettySize=auto;html=1;"
    )

    # --- Build XML ---
    root = ET.Element("mxGraphModel", {
        "dx": "240", "dy": "-80", "grid": "0", "gridSize": "10",
        "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1",
        "fold": "0", "page": "0", "pageScale": "1",
        "pageWidth": "826", "pageHeight": "1169",
        "math": "0", "shadow": "0", "lxXmlVersion": "1",
    })
    r = ET.SubElement(root, "root")

    # 0 – settings
    settings = ET.SubElement(r, "lx-settings", {"id": "0"})
    ET.SubElement(settings, "mxCell", {"style": ""})

    # 1 – base cell
    ET.SubElement(r, "mxCell", {"id": "1", "parent": "0", "style": ""})

    id_counter = 2

    def next_id():
        nonlocal id_counter
        v = str(id_counter)
        id_counter += 1
        return v

    # --- Title (id=2) ---
    tid = next_id()
    tc = ET.SubElement(r, "mxCell", {
        "id": tid, "parent": "1",
        "style": "text;strokeColor=none;fillColor=none;html=1;fontSize=24;"
                 "fontStyle=1;verticalAlign=middle;align=center;",
        "value": "Workday to Cardinus Employee Demographic Outbound Integration",
        "vertex": "1",
    })
    ET.SubElement(tc, "mxGeometry", {
        "height": "40", "width": "800", "x": "200", "y": "80", "as": "geometry",
    })

    # --- Workday HCM box (id=3) ---
    wd_id = next_id()
    wd_obj = ET.SubElement(r, "object", {
        "type": "factSheet",
        "label": WORKDAY_HCM["name"],
        "factSheetType": WORKDAY_HCM["type"],
        "factSheetId": WORKDAY_HCM["id"],
        "id": wd_id,
    })
    wd_cell = ET.SubElement(wd_obj, "mxCell", {
        "parent": "1",
        "style": BOX_STYLE.format(color=BLUE),
        "vertex": "1",
    })
    ET.SubElement(wd_cell, "mxGeometry", {
        "height": "160", "width": "160", "x": "240", "y": "280", "as": "geometry",
    })

    # --- Cardinus box (id=4) ---
    card_id = next_id()
    card_obj = ET.SubElement(r, "object", {
        "type": "factSheet",
        "label": "Cardinus<div><b>INT011</b></div>",
        "factSheetType": CARDINUS["type"],
        "factSheetId": CARDINUS["id"],
        "id": card_id,
        "lxCustomLabel": "1",
    })
    card_cell = ET.SubElement(card_obj, "mxCell", {
        "parent": "1",
        "style": BOX_STYLE.format(color=ORANGE),
        "vertex": "1",
    })
    ET.SubElement(card_cell, "mxGeometry", {
        "height": "160", "width": "170", "x": "800", "y": "280", "as": "geometry",
    })

    # --- Arrow: Workday HCM → Cardinus (id=5, Interface fact sheet) ---
    a1_id = next_id()
    a1_obj = ET.SubElement(r, "object", {
        "type": "factSheet",
        "label": INTERFACE_INT011["name"],
        "factSheetType": INTERFACE_INT011["type"],
        "factSheetId": INTERFACE_INT011["id"],
        "id": a1_id,
    })
    a1_cell = ET.SubElement(a1_obj, "mxCell", {
        "edge": "1", "parent": "1",
        "source": wd_id, "target": card_id,
        "style": EDGE_STYLE,
    })
    ET.SubElement(a1_cell, "mxGeometry", {"relative": "1", "as": "geometry"})

    # --- Flow label (id=6): below arrow ---
    fl_id = next_id()
    fl = ET.SubElement(r, "UserObject", {
        "label": (
            "EIB extracts active employee demographics<div>"
            "Document Transformation to pipe-delimited CSV</div>"
            "<div>PGP encrypted, delivered to Cardinus SFTP</div>"
        ),
        "placeholders": "1", "name": "Variable", "id": fl_id,
    })
    fl_c = ET.SubElement(fl, "mxCell", {
        "parent": "1",
        "style": "text;html=1;strokeColor=none;fillColor=none;align=center;"
                 "verticalAlign=middle;whiteSpace=wrap;overflow=hidden;fontSize=14;",
        "vertex": "1",
    })
    ET.SubElement(fl_c, "mxGeometry", {
        "height": "90", "width": "400", "x": "360", "y": "470", "as": "geometry",
    })

    # =============================================
    # Process Table – 3-column table + standalone 4th column
    # =============================================

    # --- Table container (id=7) ---
    tbl_id = next_id()
    tbl = ET.SubElement(r, "mxCell", {
        "id": tbl_id, "parent": "1",
        "style": "childLayout=tableLayout;recursiveResize=0;shadow=0;"
                 "fillColor=none;verticalAlign=top;",
        "value": "", "vertex": "1",
    })
    ET.SubElement(tbl, "mxGeometry", {
        "height": "280", "width": "890", "x": "27", "y": "590", "as": "geometry",
    })

    # --- Header row ---
    hdr_id = next_id()
    hdr = ET.SubElement(r, "mxCell", {
        "id": hdr_id, "parent": tbl_id,
        "style": "shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;"
                 "top=0;left=0;bottom=0;right=0;dropTarget=0;collapsible=0;"
                 "recursiveResize=0;expand=0;fontStyle=0;fillColor=none;strokeColor=inherit;",
        "value": "", "vertex": "1",
    })
    ET.SubElement(hdr, "mxGeometry", {
        "height": "52", "width": "890", "as": "geometry",
    })

    hdr_row_style = (
        "connectable=0;recursiveResize=0;strokeColor=inherit;"
        "fillColor=none;align=center;whiteSpace=wrap;html=1;"
    )

    headers = ["DATA EXTRACTION", "DOCUMENT TRANSFORMATION", "SFTP DELIVERY"]
    col_widths = [296, 298, 296]
    col_x = [0, 296, 594]

    for i, (header_text, w, x) in enumerate(zip(headers, col_widths, col_x)):
        cid = next_id()
        c = ET.SubElement(r, "mxCell", {
            "id": cid, "parent": hdr_id,
            "style": hdr_row_style,
            "value": header_text, "vertex": "1",
        })
        geo = ET.SubElement(c, "mxGeometry", {"height": "52", "width": str(w), "as": "geometry"})
        if x > 0:
            geo.set("x", str(x))
        ET.SubElement(geo, "mxRectangle", {
            "height": "52", "width": str(w), "as": "alternateBounds",
        })

    # --- Content row ---
    crow_id = next_id()
    crow = ET.SubElement(r, "mxCell", {
        "id": crow_id, "parent": tbl_id,
        "style": "shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;"
                 "top=0;left=0;bottom=0;right=0;dropTarget=0;collapsible=0;"
                 "recursiveResize=0;expand=0;fontStyle=0;fillColor=none;strokeColor=inherit;",
        "value": "", "vertex": "1",
    })
    ET.SubElement(crow, "mxGeometry", {
        "height": "228", "width": "890", "y": "52", "as": "geometry",
    })

    content_style = (
        "connectable=0;recursiveResize=0;strokeColor=inherit;"
        "fillColor=none;align=left;whiteSpace=wrap;html=1;verticalAlign=top;"
    )

    col1_html = (
        "<ul>"
        "<li>EIB calls custom report CR INT011</li>"
        "<li>Retrieves ~700 active employees from FA and WNSL</li>"
        "<li>Full file extract on each run</li>"
        "<li>Excludes terminated employees and contractors</li>"
        "</ul>"
    )

    col2_html = (
        "<ul>"
        "<li>XML payload converted to pipe-delimited CSV via XSLT transformation</li>"
        "<li>Character encoding: UTF-8</li>"
        "<li>Header row included in output</li>"
        "<li>File extension: .pgp</li>"
        "</ul>"
    )

    col3_html = (
        "<ul>"
        "<li>PGP encrypted file uploaded to Cardinus-hosted SFTP</li>"
        "<li>SFTP credentials stored in Workday credential store</li>"
        "<li>TLS/SSL for SFTP connection security</li>"
        "<li>Separate pre-prod and production SFTP endpoints</li>"
        "</ul>"
    )

    col_contents = [col1_html, col2_html, col3_html]

    for i, (content, w, x) in enumerate(zip(col_contents, col_widths, col_x)):
        cid = next_id()
        c = ET.SubElement(r, "mxCell", {
            "id": cid, "parent": crow_id,
            "style": content_style,
            "value": content, "vertex": "1",
        })
        geo = ET.SubElement(c, "mxGeometry", {
            "height": "228", "width": str(w), "as": "geometry",
        })
        if x > 0:
            geo.set("x", str(x))
        ET.SubElement(geo, "mxRectangle", {
            "height": "228", "width": str(w), "as": "alternateBounds",
        })

    # --- Standalone 4th column header ---
    c4h_id = next_id()
    c4h = ET.SubElement(r, "mxCell", {
        "id": c4h_id, "parent": "1",
        "style": "connectable=0;recursiveResize=0;strokeColor=inherit;"
                 "fillColor=none;align=center;whiteSpace=wrap;html=1;",
        "value": "CARDINUS IMPORT", "vertex": "1",
    })
    ET.SubElement(c4h, "mxGeometry", {
        "height": "52", "width": "296", "x": "917", "y": "590", "as": "geometry",
    })
    ET.SubElement(
        c4h.find("mxGeometry"), "mxRectangle",
        {"height": "52", "width": "296", "as": "alternateBounds"},
    )

    # --- Standalone 4th column content ---
    c4c_id = next_id()
    col4_html = (
        "<ul>"
        "<li>Cardinus polls SFTP for new files</li>"
        "<li>Auto import via LMS integration</li>"
        "<li>Import errors are outside scope of this integration</li>"
        "</ul>"
    )
    c4c = ET.SubElement(r, "mxCell", {
        "id": c4c_id, "parent": "1",
        "style": content_style,
        "value": col4_html, "vertex": "1",
    })
    ET.SubElement(c4c, "mxGeometry", {
        "height": "228", "width": "296", "x": "917", "y": "642", "as": "geometry",
    })
    ET.SubElement(
        c4c.find("mxGeometry"), "mxRectangle",
        {"height": "228", "width": "296", "as": "alternateBounds"},
    )

    # =============================================
    # Information Boxes
    # =============================================

    def add_info_box(label_html, x, y, w, h):
        nonlocal id_counter
        bid = next_id()
        obj = ET.SubElement(r, "UserObject", {
            "label": label_html,
            "placeholders": "1", "name": "Variable", "id": bid,
        })
        cell = ET.SubElement(obj, "mxCell", {
            "parent": "1",
            "style": "text;html=1;strokeColor=none;fillColor=none;align=left;"
                     "verticalAlign=top;whiteSpace=wrap;overflow=hidden;fontSize=14;",
            "vertex": "1",
        })
        ET.SubElement(cell, "mxGeometry", {
            "height": str(h), "width": str(w),
            "x": str(x), "y": str(y), "as": "geometry",
        })

    # --- Security & Technical Details ---
    security_html = (
        "<div><b>SECURITY &amp; TECHNICAL DETAILS</b></div>"
        "<div><ul>"
        "<li>Integration Type: EIB + Document Transformation</li>"
        "<li>File Format: Pipe-delimited CSV, UTF-8, full file</li>"
        "<li>Encryption: PGP for data at rest; TLS/SSL for SFTP connection</li>"
        "<li>SFTP Credentials: Stored in Workday credential store</li>"
        "<li>ISU Account: ISU_INT011</li>"
        "<li>Security Groups: ISSG INT011 Card, SBSG INT011 Card</li>"
        "<li>GDPR: Employee demographic data subject to GDPR compliance</li>"
        "<li>Data Retention: Integration outputs stored in Workday for 180 days</li>"
        "</ul></div>"
    )
    add_info_box(security_html, 27, 910, 530, 240)

    # --- System of Record ---
    sor_html = (
        "<div><b>SYSTEM OF RECORD</b></div>"
        "<div><ul>"
        "<li>Workday HCM: Source of employee demographics, contact information, organisational data</li>"
        "<li>Cardinus: Target system for health &amp; safety platform</li>"
        "<li>Scope: FA and WNSL active employees only (terminated and contractors excluded)</li>"
        "</ul></div>"
    )
    add_info_box(sor_html, 560, 910, 530, 120)

    # --- Key Attributes ---
    attrs_html = (
        "<div><b>KEY ATTRIBUTES</b></div>"
        "<div><ul>"
        "<li>Unique ID: Work Email</li>"
        "<li>Name: First Name, Last Name</li>"
        "<li>Location: Work Location</li>"
        "<li>Division: CF INT011 ST SUPERVISOR ORG custom field</li>"
        "<li>Email: Primary Work Email</li>"
        "</ul></div>"
    )
    add_info_box(attrs_html, 560, 1030, 530, 140)

    # --- Scheduling, Volumes & SLA ---
    sched_html = (
        "<div><b>SCHEDULING, VOLUMES &amp; SLA</b></div>"
        "<div><ul>"
        "<li>Schedule: Batch scheduled (frequency to be confirmed)</li>"
        "<li>On-demand rerun available to authorised users</li>"
        "<li>Volume: ~700 active employees</li>"
        "<li>File Size: Less than 1MB</li>"
        "<li>Execution Time: Less than 5 minutes</li>"
        "</ul></div>"
    )
    add_info_box(sched_html, 27, 1150, 530, 150)

    # --- Logging & Monitoring ---
    log_html = (
        "<div><b>LOGGING &amp; MONITORING</b></div>"
        "<div><ul>"
        "<li>Monitoring: Process Monitor in Workday</li>"
        "<li>Failure notifications: Email alerts to ISSG members</li>"
        "<li>Error logging: Up to 500 errors logged before processing stops</li>"
        "<li>Data Retention: 180 days for integration outputs</li>"
        "<li>Cardinus import errors: Outside scope of this integration</li>"
        "</ul></div>"
    )
    add_info_box(log_html, 27, 1300, 530, 150)

    # --- Out of Scope ---
    oos_html = (
        "<div><b>OUT OF SCOPE</b></div>"
        "<div><ul>"
        "<li>Terminated employees excluded from extract</li>"
        "<li>Real-time synchronisation not supported</li>"
        "<li>Cardinus import errors handled by Cardinus</li>"
        "<li>Training completion data not included</li>"
        "</ul></div>"
    )
    add_info_box(oos_html, 560, 1170, 530, 120)

    # --- Key Dependencies ---
    deps_html = (
        "<div><b>KEY DEPENDENCIES</b></div>"
        "<div><ul>"
        "<li>Cardinus SFTP provisioned and accessible from Workday</li>"
        "<li>PGP keys exchanged between Workday and Cardinus</li>"
        "<li>CF INT011 custom field configured in Workday</li>"
        "<li>Replaces legacy PeopleXD feed (decommissioned April 2026)</li>"
        "</ul></div>"
    )
    add_info_box(deps_html, 560, 1290, 530, 120)

    # --- Costings ---
    cost_html = (
        "<div><b>COSTINGS</b></div>"
        "<div><ul>"
        "<li>One-off: GBP 950 LMS Integration setup (Quote QUO-09182-S2L2)</li>"
        "<li>Annual: GBP 650/year Automatic Imports (Quote QUO-09182-S2L2)</li>"
        "</ul></div>"
    )
    add_info_box(cost_html, 27, 1450, 530, 100)

    # --- Environment Notes ---
    env_html = (
        "<div><b>ENVIRONMENT NOTES</b></div>"
        "<div><ul>"
        "<li>Pre-prod: Test SFTP endpoint + test PGP keys + ~50 test employees</li>"
        "<li>Production: Prod SFTP endpoint + prod PGP keys + ~700 employees</li>"
        "</ul></div>"
    )
    add_info_box(env_html, 560, 1410, 530, 100)

    # =============================================
    # Serialize
    # =============================================
    xml_str = ET.tostring(root, encoding="unicode")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml_str)

    print(f"Generated: {output_path}")


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else (
        "/Users/rpatel/Downloads/SAD_INT011_Cardinus_V1_0.xml"
    )
    generate_int011_xml(output)
