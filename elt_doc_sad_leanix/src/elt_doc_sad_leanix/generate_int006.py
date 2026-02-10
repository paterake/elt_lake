#!/usr/bin/env python3
"""
Generate LeanIX diagrams.net XML for INT006 Barclaycard Visa Credit Card Inbound
Extracted from SAD: SAD_INT006_Barclaycard_Visa_Credit_Card_v1_0.docx
Pattern: Inbound via Hyve SFTP (Vendor → Hyve SFTP → Workday)
"""

import xml.etree.ElementTree as ET
import sys


def generate_int006_xml(output_path: str):
    """Generate the INT006 Barclaycard diagram XML."""

    # --- LeanIX inventory assets ---
    BARCLAYCARD = {
        "id": "c400f9c3-0453-481f-b981-244f1543862b",
        "type": "Provider",
        "name": "Barclaycard",
    }
    HYVE_SFTP = {
        "id": "bb2e0906-47e7-4785-8a05-81e6b6c5330b",
        "type": "ITComponent",
        "name": "SFTP",
    }
    WORKDAY_FM = {
        "id": "6f852359-0d95-43c3-b642-238be59213e7",
        "type": "Application",
        "name": "Workday Financial Management",
    }
    INTERFACE_INT006 = {
        "id": "17c551bd-04b5-4397-9662-d4b78467ffae",
        "type": "Interface",
        "name": "WorkDay HCM - Barclaycard",
    }

    # --- Colours ---
    BLUE = "#497db0"
    ORANGE = "#ffa31f"
    BROWN = "#d29270"

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
        "value": "Workday Barclaycard Credit Card Transactions Integration SFTP",
        "vertex": "1",
    })
    ET.SubElement(tc, "mxGeometry", {
        "height": "40", "width": "800", "x": "200", "y": "80", "as": "geometry",
    })

    # --- Barclaycard box (id=3) ---
    bc_id = next_id()
    bc_obj = ET.SubElement(r, "object", {
        "type": "factSheet",
        "label": "Barclaycard<div><b>INT006</b></div>",
        "factSheetType": BARCLAYCARD["type"],
        "factSheetId": BARCLAYCARD["id"],
        "id": bc_id,
        "lxCustomLabel": "1",
    })
    bc_cell = ET.SubElement(bc_obj, "mxCell", {
        "parent": "1",
        "style": BOX_STYLE.format(color=ORANGE),
        "vertex": "1",
    })
    ET.SubElement(bc_cell, "mxGeometry", {
        "height": "160", "width": "170", "x": "240", "y": "280", "as": "geometry",
    })

    # --- Hyve SFTP box (id=4) ---
    sftp_id = next_id()
    sftp_obj = ET.SubElement(r, "object", {
        "type": "factSheet",
        "label": "Hyve Managed<div>SFTP Server</div>",
        "factSheetType": HYVE_SFTP["type"],
        "factSheetId": HYVE_SFTP["id"],
        "id": sftp_id,
        "lxCustomLabel": "1",
    })
    sftp_cell = ET.SubElement(sftp_obj, "mxCell", {
        "parent": "1",
        "style": BOX_STYLE.format(color=BROWN),
        "vertex": "1",
    })
    ET.SubElement(sftp_cell, "mxGeometry", {
        "height": "160", "width": "170", "x": "560", "y": "280", "as": "geometry",
    })

    # --- Workday FM box (id=5) ---
    wd_id = next_id()
    wd_obj = ET.SubElement(r, "object", {
        "type": "factSheet",
        "label": WORKDAY_FM["name"],
        "factSheetType": WORKDAY_FM["type"],
        "factSheetId": WORKDAY_FM["id"],
        "id": wd_id,
    })
    wd_cell = ET.SubElement(wd_obj, "mxCell", {
        "parent": "1",
        "style": BOX_STYLE.format(color=BLUE),
        "vertex": "1",
    })
    ET.SubElement(wd_cell, "mxGeometry", {
        "height": "160", "width": "160", "x": "880", "y": "280", "as": "geometry",
    })

    # --- Arrow: Barclaycard → SFTP (id=6, plain edge) ---
    a1_id = next_id()
    a1 = ET.SubElement(r, "mxCell", {
        "id": a1_id, "edge": "1", "parent": "1",
        "source": bc_id, "target": sftp_id,
        "style": EDGE_STYLE,
    })
    ET.SubElement(a1, "mxGeometry", {"relative": "1", "as": "geometry"})

    # --- Arrow: SFTP → Workday (id=7, Interface fact sheet) ---
    a2_id = next_id()
    a2_obj = ET.SubElement(r, "object", {
        "type": "factSheet",
        "label": INTERFACE_INT006["name"],
        "factSheetType": INTERFACE_INT006["type"],
        "factSheetId": INTERFACE_INT006["id"],
        "id": a2_id,
    })
    a2_cell = ET.SubElement(a2_obj, "mxCell", {
        "edge": "1", "parent": "1",
        "source": sftp_id, "target": wd_id,
        "style": EDGE_STYLE,
    })
    ET.SubElement(a2_cell, "mxGeometry", {"relative": "1", "as": "geometry"})

    # --- Flow label 1 (id=8): Barclaycard → SFTP ---
    fl1_id = next_id()
    fl1 = ET.SubElement(r, "UserObject", {
        "label": (
            "Barclaycard delivers Visa VCF4.4<div>scrubbed file to Hyve SFTP</div>"
            "<div>(PGP encrypted, SSH authentication)</div>"
            "<div>Daily scheduled delivery</div>"
        ),
        "placeholders": "1", "name": "Variable", "id": fl1_id,
    })
    fl1c = ET.SubElement(fl1, "mxCell", {
        "parent": "1",
        "style": "text;html=1;strokeColor=none;fillColor=none;align=center;"
                 "verticalAlign=middle;whiteSpace=wrap;overflow=hidden;fontSize=14;",
        "vertex": "1",
    })
    ET.SubElement(fl1c, "mxGeometry", {
        "height": "90", "width": "320", "x": "230", "y": "470", "as": "geometry",
    })

    # --- Flow label 2 (id=9): SFTP → Workday ---
    fl2_id = next_id()
    fl2 = ET.SubElement(r, "UserObject", {
        "label": (
            "Workday Cloud Connect retrieves<div>encrypted VCF4.4 file from SFTP</div>"
            "<div>Scheduled daily retrieval</div>"
            "<div>File decrypted using Workday PGP key</div>"
        ),
        "placeholders": "1", "name": "Variable", "id": fl2_id,
    })
    fl2c = ET.SubElement(fl2, "mxCell", {
        "parent": "1",
        "style": "text;html=1;strokeColor=none;fillColor=none;align=center;"
                 "verticalAlign=middle;whiteSpace=wrap;overflow=hidden;fontSize=14;",
        "vertex": "1",
    })
    ET.SubElement(fl2c, "mxGeometry", {
        "height": "90", "width": "320", "x": "620", "y": "470", "as": "geometry",
    })

    # =============================================
    # Process Table – 3-column table + standalone 4th column
    # =============================================

    # --- Table container (id=14) ---
    tbl_id = next_id()  # 14 if counting matches
    # The table is 3 columns: VENDOR DATA GENERATION | FILE FORMAT & ENCRYPTION | SFTP DELIVERY
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

    headers = ["VENDOR DATA GENERATION", "FILE FORMAT &amp; ENCRYPTION", "SFTP DELIVERY"]
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
        "<li>Barclaycard generates Visa VCF4.4 scrubbed files</li>"
        "<li>Two file types: Starter File (cardholder records, as needed) "
        "and Daily Transaction File (daily automated)</li>"
        "<li>Full file extract on each delivery</li>"
        "<li>Data includes: Employee ID, name, masked card number, "
        "transaction details, MCC</li>"
        "<li>Enhanced data: airline, hotel, car rental details</li>"
        "<li>Scope: FA employees only (contractors excluded)</li>"
        "</ul>"
    )

    col2_html = (
        "<ul>"
        "<li>Visa Commercial Format (VCF) Version 4.4.x specification</li>"
        "<li>Tab-delimited text file format</li>"
        "<li>Character encoding: UTF-8</li>"
        "<li>File naming convention: TBC (to be confirmed with Barclaycard)</li>"
        "<li>PGP encryption applied using Workday public key (MANDATORY)</li>"
        "<li>Environment-specific PGP keys (Sandbox, Implementation, Production)</li>"
        "</ul>"
    )

    col3_html = (
        "<ul>"
        "<li>Files delivered to FA-hosted Hyve Managed SFTP server</li>"
        "<li>SFTP endpoint: TBC (to be provisioned by FA IT)</li>"
        "<li>Authentication: SSH key authentication (OpenSSH format)</li>"
        "<li>Separate SSH keys for pre-prod and production</li>"
        "<li>File retention: Purged after successful Workday retrieval</li>"
        "<li>IP whitelisting: Barclaycard delivery IPs (TBC)</li>"
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
        "value": "WORKDAY IMPORT PROCESSING", "vertex": "1",
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
        "<li>Workday Cloud Connect scheduled integration retrieves file from SFTP</li>"
        "<li>Template: Import Visa VCF4 File (Scrubbed) - Delivered</li>"
        "<li>File decrypted using Workday private PGP key</li>"
        "<li>Validates file format (Visa VCF4.4, tab-delimited)</li>"
        "<li>Imports cardholder records and transaction records</li>"
        "<li>Associates transactions to credit cards; orphaned transactions handled</li>"
        "<li>Status: Completed, Completed with Warnings, Completed with Errors, Failed</li>"
        "<li>Notifications: Integration Administrator only for warnings/errors/failures</li>"
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
        "<li>Integration Type: Cloud Connect - Financials (Credit Card)</li>"
        "<li>Template: Import Visa VCF4 File (Scrubbed) - Delivered</li>"
        "<li>File Format: Visa Commercial Format (VCF) Version 4.4.x, Tab-delimited</li>"
        "<li>Expected Volume: Daily transaction files + periodic cardholder starter files</li>"
        "<li>Encryption: PGP for data at rest (MANDATORY); TLS/SSL for SFTP</li>"
        "<li>Authentication: SSH key authentication (environment-specific keys)</li>"
        "<li>SFTP Server: FA-hosted Hyve Managed SFTP</li>"
        "<li>File Naming: To be confirmed with Barclaycard</li>"
        "<li>Data Retention: Integration outputs stored in Workday for 180 days</li>"
        "<li>Frequency: Daily (scheduled time to be determined by FA finance team)</li>"
        "<li>ISU Account: ISU_INT006_Barclaycard_CreditCard_Inbound</li>"
        "<li>ISSG: ISSG INT006 Barclaycard Visa Credit Card and Transactions Inbound</li>"
        "</ul></div>"
    )
    add_info_box(security_html, 27, 910, 530, 320)

    # --- System of Record ---
    sor_html = (
        "<div><b>SYSTEM OF RECORD</b></div>"
        "<div><ul>"
        "<li>Workday Expenses: System of record for all credit card transaction data</li>"
        "<li>Barclaycard: Source system for Visa VCF4.4 credit card transaction files</li>"
        "<li>Scope: The Football Association Limited employees only</li>"
        "</ul></div>"
    )
    add_info_box(sor_html, 560, 910, 530, 100)

    # --- Key Attributes Synchronized ---
    attrs_html = (
        "<div><b>KEY ATTRIBUTES SYNCHRONIZED</b></div>"
        "<div><ul>"
        "<li>Cardholder Information: Employee ID, Name, Masked Card Number</li>"
        "<li>Transaction Details: Transaction Date, Post Date, Merchant Name, Amount</li>"
        "<li>Merchant Category: Merchant Category Code (MCC) for expense classification</li>"
        "<li>Enhanced Airline Data: Ticket Number, Passenger Name, Origin, Destination</li>"
        "<li>Enhanced Hotel Data: Check-in/out Dates, Hotel Name, Room Rate</li>"
        "<li>Enhanced Car Rental Data: Agreement Number, Dates, Locations</li>"
        "</ul></div>"
    )
    add_info_box(attrs_html, 560, 1010, 530, 140)

    # --- Key Dependencies ---
    deps_html = (
        "<div><b>KEY DEPENDENCIES</b></div>"
        "<div><ul>"
        "<li>Barclaycard must configure automated daily delivery to FA SFTP</li>"
        "<li>FA IT must provision SFTP server with directories and credentials</li>"
        "<li>PGP key exchange required between Workday and Barclaycard</li>"
        "<li>Environment-specific SSH/PGP keys for Sandbox, Implementation, Production</li>"
        "<li>Downstream journal posting to Great Plains is out of scope</li>"
        "</ul></div>"
    )
    add_info_box(deps_html, 560, 1150, 530, 120)

    # --- Scheduling, Volumes & SLA ---
    sched_html = (
        "<div><b>SCHEDULING, VOLUMES &amp; SLA</b></div>"
        "<div><ul>"
        "<li>Schedule: Daily automated at time determined by FA finance team</li>"
        "<li>Manual launch available to authorised users for ad-hoc processing</li>"
        "<li>Starter File (cardholder records): As needed / initial load</li>"
        "<li>Daily Transaction File: Daily automated schedule</li>"
        "<li>Full file extract on each delivery</li>"
        "<li>Go-Live Target: April 1, 2026</li>"
        "</ul></div>"
    )
    add_info_box(sched_html, 27, 1230, 530, 150)

    # --- Logging & Monitoring ---
    log_html = (
        "<div><b>LOGGING &amp; MONITORING</b></div>"
        "<div><ul>"
        "<li>Integration event statuses: Completed, Completed with Warnings, "
        "Completed with Errors, Failed, Aborted</li>"
        "<li>Error threshold: Up to 500 errors logged before processing stops</li>"
        "<li>Notifications: Integration Administrator notified for warnings/errors/failures only</li>"
        "<li>Daily monitoring: Finance and Expenses teams via Process Monitor</li>"
        "<li>Orphaned transactions: Created for transactions with no matching employee</li>"
        "<li>First-line support: FA internal teams; escalation to AMS+ post-hypercare</li>"
        "</ul></div>"
    )
    add_info_box(log_html, 27, 1380, 530, 160)

    # --- Out of Scope ---
    oos_html = (
        "<div><b>OUT OF SCOPE</b></div>"
        "<div><ul>"
        "<li>Downstream journal posting from Workday to Great Plains (separate solution required)</li>"
        "<li>Contractors excluded from cardholder population</li>"
        "<li>Hypercare support limited to agreed period per Statement of Work</li>"
        "</ul></div>"
    )
    add_info_box(oos_html, 560, 1270, 530, 100)

    # --- Environment Notes ---
    env_html = (
        "<div><b>ENVIRONMENT NOTES</b></div>"
        "<div><ul>"
        "<li>Environment-specific SFTP endpoints, directories, and SSH keys (TBC by FA IT)</li>"
        "<li>Separate PGP keys per environment: Sandbox, Implementation, Production</li>"
        "<li>SSH and PGP keys must be regenerated for each Workday environment migration</li>"
        "<li>Testing via Barclaycard test environment for UAT file validation</li>"
        "</ul></div>"
    )
    add_info_box(env_html, 560, 1370, 530, 120)

    # =============================================
    # Serialize
    # =============================================
    xml_str = ET.tostring(root, encoding="unicode")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml_str)

    print(f"Generated: {output_path}")


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else (
        "/Users/rpatel/Downloads/SAD_INT006_Barclaycard_Visa_Credit_Card_v1_0.xml"
    )
    generate_int006_xml(output)
