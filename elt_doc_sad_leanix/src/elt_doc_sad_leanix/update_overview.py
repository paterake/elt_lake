import argparse
import os
import re
import math
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET


WORKDAY_LABEL_SUBSTR = "Workday Human Capital Management"
WORKDAY_COLOR = "#497db0"
APPLICATION_COLOR = "#497db0"
PROVIDER_COLOR = "#ffa31f"
ITCOMP_COLOR = "#d29270"
EDGE_STYLE = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1"
BOX_STYLE = "shape=label;perimeter=rectanglePerimeter;fontSize=11;fontFamily=72, Helvetica Neue, Helvetica, Arial, sans-serif;align=center;verticalAlign=middle;fillColor={fill};strokeColor={fill};fontColor=#ffffff;startSize=45;whiteSpace=wrap;rounded=1;arcSize=10;html=1"


def _text(elem):
    return "".join(elem.itertext())


def _clean_label(label):
    # Insert space before block-level closing/opening tags to preserve word boundaries
    text = label or ""
    text = re.sub(r"</?(div|br|p|li|ul|ol|font|span)\b[^>]*>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", text).strip()


def _find_workday(root):
    for obj in root.findall(".//object"):
        if obj.get("type") == "factSheet" and obj.get("factSheetType") == "Application":
            lbl = _clean_label(obj.get("label", ""))
            if "Workday" in lbl and "Human Capital Management" in lbl:
                return obj
    return None


def _get_geometry(elem):
    geo = elem.find(".//mxGeometry")
    if geo is None:
        return None
    return {
        "x": float(geo.get("x", "0")),
        "y": float(geo.get("y", "0")),
        "width": float(geo.get("width", "0")),
        "height": float(geo.get("height", "0")),
        "elem": geo,
    }


def _collect_first_row_boxes(root, workday_id):
    boxes = []
    for edge in root.findall(".//mxCell"):
        if edge.get("edge") == "1" and edge.get("source") == workday_id:
            target = edge.get("target")
            if not target:
                continue
            obj = root.find(f".//object[@id='{target}']")
            if obj is not None:
                cell = obj.find(".//mxCell")
                geo = _get_geometry(cell)
                if geo:
                    boxes.append((target, geo))
                continue
            # Also check plain mxCell vertex elements (e.g. INT018/INT019)
            cell = root.find(f".//mxCell[@id='{target}']")
            if cell is not None and cell.get("vertex") == "1":
                geo = _get_geometry(cell)
                if geo:
                    boxes.append((target, geo))
    return boxes


def _int_id_from_filename(filename):
    """Extract INT ID from filename like COR_V00.01_INT006_..., preferring it over content."""
    m = re.search(r"(INT\d{3})", str(filename))
    return m.group(1) if m else None

def _extract_int_ids_from_xml(tree):
    ids = set()
    for obj in tree.findall(".//object"):
        lbl = _clean_label(obj.get("label", ""))
        for m in re.findall(r"INT\d{3}", lbl):
            ids.add(m)
    for uo in tree.findall(".//UserObject"):
        lbl = _clean_label(uo.get("label", ""))
        for m in re.findall(r"INT\d{3}", lbl):
            ids.add(m)
    # Also check plain mxCell value attributes (some XMLs use these instead of object tags)
    for cell in tree.findall(".//mxCell"):
        val = _clean_label(cell.get("value", ""))
        for m in re.findall(r"INT\d{3}", val):
            ids.add(m)
    return ids


def _already_present_ints(root):
    present = set()
    for obj in root.findall(".//object"):
        lbl = _clean_label(obj.get("label", ""))
        for m in re.findall(r"INT\d{3}", lbl):
            present.add(m)
    for uo in root.findall(".//UserObject"):
        lbl = _clean_label(uo.get("label", ""))
        for m in re.findall(r"INT\d{3}", lbl):
            present.add(m)
    return present

def _already_present_ints_by_text(xml_path: Path):
    try:
        text = xml_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return set()
    return set(re.findall(r"INT\d{3}", text))

def _collect_factsheet_id_map(root):
    """Return dict mapping (factSheetId, factSheetType) → element ID for all boxes."""
    fsid_map = {}
    for obj in root.findall(".//object"):
        fsid = obj.get("factSheetId")
        ftype = obj.get("factSheetType")
        if fsid and obj.get("type") == "factSheet" and ftype:
            cell = obj.find(".//mxCell")
            if cell is not None and cell.get("vertex") == "1":
                fsid_map[(fsid, ftype)] = obj.get("id")
    for cell in root.findall(".//mxCell"):
        fsid = cell.get("factSheetId")
        if fsid and cell.get("vertex") == "1":
            # Plain mxCells don't have factSheetType, use generic key
            if (fsid, None) not in fsid_map:
                fsid_map[(fsid, None)] = cell.get("id")
    return fsid_map

def _fsid_lookup(fsid_map, fsid, ftype):
    """Look up element ID by factSheetId and type, with fallback to type=None."""
    if not fsid:
        return None
    return fsid_map.get((fsid, ftype)) or fsid_map.get((fsid, None))

def _already_present_ints_by_objects(root):
    present = set()
    # Only consider factSheet objects (diagram boxes), not notes or arbitrary text
    for obj in root.findall(".//object"):
        if obj.get("type") != "factSheet":
            continue
        lbl = _clean_label(obj.get("label", ""))
        for m in re.findall(r"INT\d{3}", lbl):
            present.add(m)
    # Additionally consider interface-wrapped edges with labels containing INT###
    for obj in root.findall(".//object"):
        if obj.get("type") == "factSheet" and obj.get("factSheetType") == "Interface":
            lbl = _clean_label(obj.get("label", ""))
            for m in re.findall(r"INT\d{3}", lbl):
                present.add(m)
    # Also scan plain mxCell vertex elements for INT IDs (e.g. INT018/INT019)
    for cell in root.findall(".//mxCell"):
        if cell.get("vertex") != "1":
            continue
        style = cell.get("style", "")
        if style.startswith("text;") or "connectable=0" in style or "childLayout" in style:
            continue
        val = _clean_label(cell.get("value", ""))
        for m in re.findall(r"INT\d{3}", val):
            present.add(m)
    return present

def _choose_vendor_and_intermediary(tree):
    vendor = None
    intermediary = None
    for obj in tree.findall(".//object"):
        if obj.get("type") != "factSheet":
            continue
        lbl = _clean_label(obj.get("label", ""))
        if "Workday" in lbl and "Human Capital Management" in lbl:
            continue
        if "SFTP" in lbl or "Gateway" in lbl:
            intermediary = lbl
        else:
            vendor = lbl
    return vendor, intermediary


def _add_box(root, label, x, y, width=160, height=160, fill=APPLICATION_COLOR, fact_type="Application", fact_id=None):
    new_id = _next_id(root)
    obj = ET.SubElement(root.find("root"), "object", {
        "type": "factSheet",
        "label": label,
        "factSheetType": fact_type,
        "factSheetId": fact_id or new_id,
        "id": new_id,
    })
    cell = ET.SubElement(obj, "mxCell", {
        "parent": "1",
        "style": BOX_STYLE.format(fill=fill),
        "vertex": "1",
    })
    ET.SubElement(cell, "mxGeometry", {
        "height": str(height),
        "width": str(width),
        "x": str(x),
        "y": str(y),
        "as": "geometry",
    })
    return new_id


def _add_edge(root, source, target, bidirectional=False):
    new_id = _next_id(root)
    style = EDGE_STYLE
    if bidirectional:
        style += ";startArrow=classic;endArrow=classic"
    edge = ET.SubElement(root.find("root"), "mxCell", {
        "id": new_id,
        "edge": "1",
        "parent": "1",
        "source": source,
        "target": target,
        "style": style,
    })
    ET.SubElement(edge, "mxGeometry", {"relative": "1", "as": "geometry"})
    return new_id

def _add_edge_if_missing(root, module_id, intermediary_id, direction):
    """Add edge between module and intermediary if one doesn't already exist."""
    for cell in root.findall(".//mxCell"):
        if cell.get("edge") != "1":
            continue
        src, trg = cell.get("source"), cell.get("target")
        if {src, trg} == {module_id, intermediary_id}:
            return  # edge already exists
    if direction == "inbound":
        _add_edge(root, intermediary_id, module_id)
    elif direction == "bidirectional":
        _add_edge(root, intermediary_id, module_id, bidirectional=True)
    else:
        _add_edge(root, module_id, intermediary_id)


def _next_id(root):
    used = set()
    for e in root.findall(".//mxCell"):
        if e.get("id"):
            used.add(int(e.get("id")))
    for e in root.findall(".//object"):
        if e.get("id"):
            try:
                used.add(int(e.get("id")))
            except ValueError:
                pass
    for e in root.findall(".//UserObject"):
        if e.get("id"):
            try:
                used.add(int(e.get("id")))
            except ValueError:
                pass
    nxt = 2
    while nxt in used:
        nxt += 1
    return str(nxt)

def _set_single_page(root):
    model = root
    if model.tag != "mxGraphModel":
        model = root.getroot()
    max_right = 0.0
    max_bottom = 0.0
    for geo in root.findall(".//mxGeometry"):
        try:
            x = float(geo.get("x", "0"))
            y = float(geo.get("y", "0"))
            w = float(geo.get("width", "0"))
            h = float(geo.get("height", "0"))
            max_right = max(max_right, x + w)
            max_bottom = max(max_bottom, y + h)
        except Exception:
            continue
    margin = 100
    model.set("page", "1")
    model.set("pageScale", "1")
    model.set("pageWidth", str(int(max_right + margin)))
    model.set("pageHeight", str(int(max_bottom + margin)))

def _wrap_mxfile(root, name="Overview"):
    mxfile = ET.Element("mxfile")
    diagram = ET.SubElement(mxfile, "diagram", {"name": name})
    diagram.append(root)
    return mxfile

def _extract_list_items_from_html(html):
    items = []
    for m in re.finditer(r"<li>(.*?)</li>", html or "", flags=re.IGNORECASE | re.DOTALL):
        txt = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        if txt:
            items.append(txt)
    return items

def _extract_notes(tree):
    notes = {
        "data_protection": set(),
        "protocols": set(),
        "legal_entities": set(),
        "assessment": set(),
        "security_framework": set(),
        "volumes": set(),
        "costings": set(),
        "environment": set(),
        "constraints": set(),
        "dependencies": set(),
    }
    for uo in tree.findall(".//UserObject"):
        lbl = uo.get("label", "") or ""
        plain = _clean_label(lbl)
        items = _extract_list_items_from_html(lbl)
        tgt = None
        if "security" in plain:
            tgt = "security_framework"
        elif "data protection" in plain or "encryption" in plain:
            tgt = "data_protection"
        elif "protocol" in plain or "api" in plain or "sftp" in plain or "https" in plain:
            tgt = "protocols"
        elif "legal entity" in plain:
            tgt = "legal_entities"
        elif "assessment" in plain:
            tgt = "assessment"
        elif "volume" in plain or "frequency" in plain or "scheduled" in plain:
            tgt = "volumes"
        elif "environment" in plain:
            tgt = "environment"
        elif "cost" in plain or "licensing" in plain:
            tgt = "costings"
        elif "constraint" in plain or "limitation" in plain:
            tgt = "constraints"
        elif "dependenc" in plain or "gateway" in plain or "sftp" in plain:
            tgt = "dependencies"
        if tgt:
            for it in items:
                notes[tgt].add(it)
        else:
            for it in items:
                low = it.lower()
                if any(k in low for k in ["pgp", "encryption", "tls", "ssl"]):
                    notes["data_protection"].add(it)
                elif any(k in low for k in ["sftp", "https", "api", "eib", "oauth", "webhook"]):
                    notes["protocols"].add(it)
                elif any(k in low for k in ["frequency", "daily", "weekly", "monthly", "volume"]):
                    notes["volumes"].add(it)
    return {k: sorted(v) for k, v in notes.items()}

def _aggregate_notes(input_dir, overview_filename):
    agg = {
        "data_protection": set(),
        "protocols": set(),
        "legal_entities": set(),
        "assessment": set(),
        "security_framework": set(),
        "volumes": set(),
        "costings": set(),
        "environment": set(),
        "constraints": set(),
        "dependencies": set(),
    }
    for xml_path in sorted(Path(os.path.expanduser(input_dir)).glob("*.xml")):
        if "Overview" in xml_path.name:
            continue
        try:
            t = ET.parse(xml_path)
        except Exception:
            continue
        notes = _extract_notes(t)
        for k in agg.keys():
            agg[k].update(notes.get(k, []))
    return {k: sorted(v) for k, v in agg.items()}

def _add_notes_box(root, title, items, x, y, width=530, height=240):
    content = f"<div><b>{title}</b></div><div><ul>" + "".join(f"<li>{it}</li>" for it in items) + "</ul></div>"
    new_id = _next_id(root)
    obj = ET.SubElement(root.find("root"), "UserObject", {
        "label": content,
        "placeholders": "1",
        "name": "Variable",
        "id": new_id,
    })
    cell = ET.SubElement(obj, "mxCell", {
        "parent": "1",
        "style": "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;whiteSpace=wrap;overflow=hidden;fontSize=14;",
        "vertex": "1",
    })
    ET.SubElement(cell, "mxGeometry", {
        "height": str(height),
        "width": str(width),
        "x": str(x),
        "y": str(y),
        "as": "geometry",
    })
    return new_id

_NOTE_HEADERS = [
    "data protection", "integration protocols", "legal entity",
    "integration assessment", "security", "compliance framework",
    "data volumes", "performance metrics",
]

def _remove_existing_notes(root):
    """Remove old note-style text boxes (plain mxCells and UserObjects) that match note headers."""
    root_elem = root.find("root")
    if root_elem is None:
        return
    to_remove = []
    for cell in root_elem.findall("mxCell"):
        if cell.get("vertex") != "1":
            continue
        style = cell.get("style", "")
        if "text;" not in style and "overflow" not in style:
            continue
        val = _clean_label(cell.get("value", "")).lower()
        if any(h in val for h in _NOTE_HEADERS):
            to_remove.append(cell)
    for uo in root_elem.findall("UserObject"):
        lbl = _clean_label(uo.get("label", "")).lower()
        if any(h in lbl for h in _NOTE_HEADERS):
            to_remove.append(uo)
    for elem in to_remove:
        root_elem.remove(elem)

def _add_notes_to_overview(root, workday_geo, agg_notes):
    left_x = 40
    start_y = int(workday_geo["y"] + workday_geo["height"] + 300)
    step = 260
    sections = [
        ("Data Protection", agg_notes.get("data_protection", [])),
        ("Integration Protocols", agg_notes.get("protocols", [])),
        ("Legal Entity Segregation", agg_notes.get("legal_entities", [])),
        ("Integration Assessment", agg_notes.get("assessment", [])),
        ("Security & Compliance Framework", agg_notes.get("security_framework", [])),
    ]
    y = start_y
    for title, items in sections:
        if items:
            _add_notes_box(root, title, items, left_x, y)
            y += step
    right_x = int(workday_geo["x"] + workday_geo["width"] + 200)
    volumes = agg_notes.get("volumes", [])
    if volumes:
        _add_notes_box(root, "Data Volumes & Performance Metrics", volumes, right_x, start_y, width=600, height=300)

def _extract_entities(tree):
    """Extract vendor, intermediary, and Workday module from an individual integration XML."""
    vendor = None
    intermediary = None
    module_label = None
    
    # Track XML IDs for direction detection
    workday_oid = None
    vendor_oid = None
    intermediary_oid = None

    for obj in tree.findall(".//object"):
        if obj.get("type") != "factSheet":
            continue
        lbl = obj.get("label", "") or ""
        t = obj.get("factSheetType", "")
        fsid = obj.get("factSheetId")
        clean = _clean_label(lbl)
        clean_lower = clean.lower()
        
        # Identify entities and capture their XML IDs
        if "workday" in clean_lower:
            workday_oid = obj.get("id")
            if "financial management" in clean_lower:
                module_label = "Workday Financial Management"
            elif "human capital management" in clean_lower:
                module_label = "Workday Human Capital Management"
            continue
        if t == "ITComponent" or "sftp" in clean_lower or "gateway" in clean_lower:
            intermediary = {"label": lbl, "type": "ITComponent", "id": fsid, "color": ITCOMP_COLOR}
            intermediary_oid = obj.get("id")
            continue
        if t in ("Application", "Provider"):
            color = APPLICATION_COLOR if t == "Application" else PROVIDER_COLOR
            vendor = {"label": lbl, "type": t, "id": fsid, "color": color}
            vendor_oid = obj.get("id")
            
    # Fallback: check plain mxCell vertex elements if no vendor/intermediary found via factSheet objects
    if vendor is None and intermediary is None:
        for cell in tree.findall(".//mxCell"):
            if cell.get("vertex") != "1":
                continue
            val = _clean_label(cell.get("value", ""))
            val_lower = val.lower()
            if not val or "workday" in val_lower:
                continue
            # Skip title/heading cells (large font text labels)
            style = cell.get("style", "")
            if "fontSize=24" in style or "fontSize=18" in style:
                continue
            # Skip table/detail cells
            if "tableRow" in style or "connectable=0" in style or "childLayout=tableLayout" in style:
                continue
            cid = cell.get("id")
            # Skip text/description cells (no fill, no shape - just annotation boxes)
            style = cell.get("style", "")
            if style.startswith("text;"):
                continue
            if intermediary is None and ("sftp" in val_lower or "gateway" in val_lower):
                # Strip embedded INT IDs from intermediary labels (vendor box carries the ID)
                clean_val = re.sub(r"\s*INT\d{3}\s*", " ", val).strip()
                intermediary = {"label": clean_val, "type": "ITComponent", "id": None, "color": ITCOMP_COLOR}
                intermediary_oid = cid
            elif vendor is None:
                vendor = {"label": val, "type": "Application", "id": None, "color": APPLICATION_COLOR}
                vendor_oid = cid

    # Default module if not explicitly found
    if module_label is None:
        module_label = "Workday Human Capital Management"

    # Determine direction
    direction = "outbound" # Default
    workday_edge_found = False
    
    # Check for bidirectional edges first
    inbound_found = False
    outbound_found = False

    if workday_oid:
        for cell in tree.findall(".//mxCell"):
            src = cell.get("source")
            trg = cell.get("target")
            if not src or not trg: continue
            
            if src == workday_oid:
                if trg == intermediary_oid or trg == vendor_oid:
                    outbound_found = True
                    workday_edge_found = True
            elif trg == workday_oid:
                if src == intermediary_oid or src == vendor_oid:
                    inbound_found = True
                    workday_edge_found = True

    if not workday_edge_found and vendor_oid and intermediary_oid:
        for cell in tree.findall(".//mxCell"):
            src = cell.get("source")
            trg = cell.get("target")
            if not src or not trg: continue
            
            if src == vendor_oid and trg == intermediary_oid:
                inbound_found = True
            elif src == intermediary_oid and trg == vendor_oid:
                outbound_found = True
    
    if inbound_found and outbound_found:
        direction = "bidirectional"
    elif inbound_found:
        direction = "inbound"
    elif outbound_found:
        direction = "outbound"
    
    return vendor, intermediary, module_label, direction


def _create_root():
    root = ET.Element("mxGraphModel", {
        "dx": "240",
        "dy": "-80",
        "grid": "0",
        "gridSize": "10",
        "guides": "1",
        "tooltips": "1",
        "connect": "1",
        "arrows": "1",
        "fold": "0",
        "page": "0",
        "pageScale": "1",
        "pageWidth": "826",
        "pageHeight": "1169",
        "math": "0",
        "shadow": "0",
        "lxXmlVersion": "1",
    })
    r = ET.SubElement(root, "root")
    s = ET.SubElement(r, "lx-settings", {"id": "0"})
    ET.SubElement(s, "mxCell", {"style": ""})
    ET.SubElement(r, "mxCell", {"id": "1", "parent": "0", "style": ""})
    return root


def create_overview(input_dir, output_path):
    input_dir = Path(os.path.expanduser(input_dir))
    files = [p for p in input_dir.glob("*.xml") if "Overview" not in p.name]
    root = _create_root()
    
    # Group integrations by Workday module
    groups = {
        "Workday Human Capital Management": [],
        "Workday Financial Management": [],
    }
    processed_int_ids = set()
    for xml_path in sorted(files):
        try:
            t = ET.parse(xml_path)
        except Exception:
            continue
        ints = _extract_int_ids_from_xml(t)
        if not ints:
            int_id = _int_id_from_filename(xml_path.name)
            if not int_id:
                continue
        else:
            int_id = sorted(ints)[0]
            
        if int_id in processed_int_ids:
            continue
        processed_int_ids.add(int_id)
        vendor, intermediary, module_label, direction = _extract_entities(t)
        groups.setdefault(module_label, [])
        groups[module_label].append({"int_id": int_id, "vendor": vendor, "intermediary": intermediary, "direction": direction})

    # Layout constants
    MAX_COLS = 6
    COL_WIDTH = 350
    ROW_HEIGHT = 450
    MODULE_HEADER_HEIGHT = 200
    MODULE_SPACING = 150
    START_X = 40
    
    current_y = 50
    module_order = ["Workday Human Capital Management", "Workday Financial Management"]
    
    fsid_map = {}  # (factSheetId, factSheetType) -> element ID for intermediary dedup
    
    # Track bounds for final notes placement
    max_y = 0
    max_x = 0
    
    for module in module_order:
        entries = groups.get(module, [])
        count = len(entries)
        
        num_rows = math.ceil(count / MAX_COLS) if count > 0 else 1
        num_cols = min(count, MAX_COLS) if count > 0 else 1
        
        mod_width = max(1440, num_cols * COL_WIDTH)
        
        # Create Module Header Box
        workday_id = _add_box(
            root,
            f"{module}\n(System of Record)",
            START_X,
            current_y,
            width=mod_width,
            height=MODULE_HEADER_HEIGHT,
            fill=WORKDAY_COLOR,
            fact_type="Application",
            fact_id=None,
        )
        
        # Place Integrations
        start_int_y = current_y + MODULE_HEADER_HEIGHT + 80
        
        for i, entry in enumerate(entries):
            row = i // MAX_COLS
            col = i % MAX_COLS
            
            x_pos = START_X + col * COL_WIDTH + 20
            y_pos = start_int_y + row * ROW_HEIGHT
            
            int_id = entry["int_id"]
            vendor = entry["vendor"]
            intermediary = entry["intermediary"]
            direction = entry["direction"]
            
            if intermediary:
                # Reuse existing intermediary box if same factSheetId+type
                existing_inter = _fsid_lookup(fsid_map, intermediary["id"], intermediary["type"])
                if existing_inter:
                    inter_id = existing_inter
                    _add_edge_if_missing(root, workday_id, inter_id, direction)
                else:
                    inter_id = _add_box(
                        root,
                        intermediary["label"],
                        x_pos,
                        y_pos,
                        width=170,
                        height=160,
                        fill=intermediary["color"],
                        fact_type=intermediary["type"],
                        fact_id=intermediary["id"],
                    )
                    if intermediary["id"]:
                        fsid_map[(intermediary["id"], intermediary["type"])] = inter_id
                    if direction == "inbound":
                        _add_edge(root, inter_id, workday_id)
                    elif direction == "bidirectional":
                        _add_edge(root, inter_id, workday_id, bidirectional=True)
                    else:
                        _add_edge(root, workday_id, inter_id)
                
                if vendor:
                    vend_id = _add_box(
                        root,
                        f"{vendor['label']}\n{int_id}",
                        x_pos,
                        y_pos + 200,
                        width=160,
                        height=160,
                        fill=vendor["color"],
                        fact_type=vendor["type"],
                        fact_id=vendor["id"],
                    )
                    if direction == "inbound":
                        _add_edge(root, vend_id, inter_id)
                    elif direction == "bidirectional":
                        _add_edge(root, vend_id, inter_id, bidirectional=True)
                    else:
                        _add_edge(root, inter_id, vend_id)
            else:
                label = f"Integration {int_id}"
                if vendor:
                    label = f"{vendor['label']}\n{int_id}"
                
                vend_id = _add_box(
                    root,
                    label,
                    x_pos,
                    y_pos,
                    width=160,
                    height=160,
                    fill=vendor["color"] if vendor else APPLICATION_COLOR,
                    fact_type=vendor["type"] if vendor else "Application",
                    fact_id=vendor["id"] if vendor else None,
                )
                
                if direction == "inbound":
                    _add_edge(root, vend_id, workday_id)
                elif direction == "bidirectional":
                    _add_edge(root, vend_id, workday_id, bidirectional=True)
                else:
                    _add_edge(root, workday_id, vend_id)

        # Update current_y for next module
        section_height = MODULE_HEADER_HEIGHT + 80 + (num_rows * ROW_HEIGHT)
        current_y += section_height + MODULE_SPACING
        
        max_x = max(max_x, START_X + mod_width)
        max_y = current_y

    target_path = Path(os.path.expanduser(output_path))
    if target_path.parent and not target_path.parent.exists():
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
    agg_notes = _aggregate_notes(input_dir, "")
    notes_geo = {
        "x": START_X,
        "y": max_y,
        "width": max_x,
        "height": 0,
    }
    _add_notes_to_overview(root, notes_geo, agg_notes)
    _set_single_page(root)
    wrapper = _wrap_mxfile(root, "Workday Overview")
    ET.ElementTree(wrapper).write(str(target_path), encoding="utf-8", xml_declaration=False)
    return len(files)


def _find_module_box(root, module_substr):
    for obj in root.findall(".//object"):
        if obj.get("type") == "factSheet" and obj.get("factSheetType") == "Application":
            lbl = _clean_label(obj.get("label", ""))
            if module_substr.lower() in lbl.lower():
                return obj
    return None


def update_overview(input_dir, overview_filename, output_path=None, dest_dir=None):
    input_dir = Path(os.path.expanduser(input_dir))
    overview_path = input_dir / overview_filename
    tree = ET.parse(overview_path)
    root = tree.getroot()
    hcm_obj = _find_module_box(root, "Human Capital Management")
    fm_obj = _find_module_box(root, "Financial Management")
    if hcm_obj is None:
        raise RuntimeError("Workday HCM box not found in overview")
    # Create FM box if missing
    if fm_obj is None:
        hcm_cell = hcm_obj.find(".//mxCell")
        hcm_geo = _get_geometry(hcm_cell)
        fm_obj_id = _add_box(
            root,
            "Workday Financial Management\n(System of Record)",
            int(hcm_geo["x"]),
            int(hcm_geo["y"] + hcm_geo["height"] + 350),
            width=1440,
            height=250,
            fill=WORKDAY_COLOR,
            fact_type="Application",
            fact_id=None,
        )
        fm_obj = root.find(f".//object[@id='{fm_obj_id}']")
    # Compute per-module layout refs
    def module_layout(obj):
        cell = obj.find(".//mxCell")
        geo = _get_geometry(cell)
        fr = _collect_first_row_boxes(root, obj.get("id"))
        y_vals = [g["y"] for _, g in fr] or [geo["y"] + 450]
        y_ref = Counter(y_vals).most_common(1)[0][0]
        max_x = max([g["x"] for _, g in fr], default=geo["x"])
        return geo, y_ref, max_x, len(fr)
    hcm_geo, hcm_y_ref, hcm_max_x, hcm_cols = module_layout(hcm_obj)
    fm_geo, fm_y_ref, fm_max_x, fm_cols = module_layout(fm_obj)
    # Detect existing integrations by diagram objects/edges, not free text
    present_ints = _already_present_ints_by_objects(root)
    fsid_map = _collect_factsheet_id_map(root)
    hcm_added = 0
    fm_added = 0
    added_total = 0
    for xml_path in sorted(input_dir.glob("*.xml")):
        if xml_path.name == overview_filename or "Overview" in xml_path.name:
            continue
        t = ET.parse(xml_path)
        ints = _extract_int_ids_from_xml(t)
        if not ints:
            continue
        int_id = _int_id_from_filename(xml_path.name) or sorted(ints)[0]
        if int_id in present_ints:
            continue
        vendor, intermediary, module_label, direction = _extract_entities(t)
        if "Financial Management" in module_label:
            base_geo, y_ref, max_x, cols = fm_geo, fm_y_ref, fm_max_x, fm_cols
            top_id = fm_obj.get("id")
            col_offset = fm_added
            is_fm = True
        else:
            base_geo, y_ref, max_x, cols = hcm_geo, hcm_y_ref, hcm_max_x, hcm_cols
            top_id = hcm_obj.get("id")
            col_offset = hcm_added
            is_fm = False

        # Track whether we actually need a new column
        needs_new_column = True
        col_x = (max_x if cols else base_geo["x"]) + 320 * (cols + col_offset + 1)
        if intermediary:
            # Check if intermediary already exists in overview by factSheetId+type
            existing_inter = _fsid_lookup(fsid_map, intermediary["id"], intermediary["type"])
            if existing_inter:
                inter_id = existing_inter
                needs_new_column = False
                # Still need to connect intermediary → module if not already connected
                _add_edge_if_missing(root, top_id, inter_id, direction)
            else:
                inter_id = _add_box(
                    root,
                    intermediary["label"],
                    col_x,
                    y_ref,
                    width=170,
                    height=160,
                    fill=intermediary["color"],
                    fact_type=intermediary["type"],
                    fact_id=intermediary["id"],
                )
                if intermediary["id"]:
                    fsid_map[(intermediary["id"], intermediary["type"])] = inter_id
                if direction == "inbound":
                    _add_edge(root, inter_id, top_id)
                elif direction == "bidirectional":
                    _add_edge(root, inter_id, top_id, bidirectional=True)
                else:
                    _add_edge(root, top_id, inter_id)
            if vendor:
                # Place vendor below intermediary
                if not needs_new_column:
                    # Get x position of existing intermediary for alignment
                    inter_obj = root.find(f".//object[@id='{inter_id}']")
                    if inter_obj is not None:
                        inter_geo = _get_geometry(inter_obj.find(".//mxCell"))
                        vend_x = inter_geo["x"] if inter_geo else col_x
                    else:
                        inter_cell = root.find(f".//mxCell[@id='{inter_id}']")
                        inter_geo = _get_geometry(inter_cell) if inter_cell is not None else None
                        vend_x = inter_geo["x"] if inter_geo else col_x
                else:
                    vend_x = col_x
                vend_id = _add_box(
                    root,
                    f"{vendor['label']}\n{int_id}",
                    vend_x,
                    y_ref + 200,
                    width=160,
                    height=160,
                    fill=vendor["color"],
                    fact_type=vendor["type"],
                    fact_id=vendor["id"],
                )
                if direction == "inbound":
                    _add_edge(root, vend_id, inter_id)
                elif direction == "bidirectional":
                    _add_edge(root, vend_id, inter_id, bidirectional=True)
                else:
                    _add_edge(root, inter_id, vend_id)
        else:
            if vendor is None:
                vendor = f"Integration {int_id}"
            vend_id = _add_box(
                root,
                f"{vendor['label']}\n{int_id}" if isinstance(vendor, dict) else f"{vendor}\n{int_id}",
                col_x,
                y_ref,
                width=160,
                height=160,
                fill=(vendor["color"] if isinstance(vendor, dict) else APPLICATION_COLOR),
                fact_type=(vendor["type"] if isinstance(vendor, dict) else "Application"),
                fact_id=(vendor["id"] if isinstance(vendor, dict) else None),
            )
            if direction == "inbound":
                _add_edge(root, vend_id, top_id)
            else:
                _add_edge(root, top_id, vend_id)

        if needs_new_column:
            if is_fm:
                fm_added += 1
            else:
                hcm_added += 1
        added_total += 1
        present_ints.add(int_id)

    if added_total:
        # Extend both module boxes by added columns
        if hcm_added:
            hcm_obj.find(".//mxCell/mxGeometry").set("width", str(hcm_geo["width"] + 320 * hcm_added))
        if fm_added:
            fm_obj.find(".//mxCell/mxGeometry").set("width", str(fm_geo["width"] + 320 * fm_added))
            
        if output_path is not None:
            target_path = Path(os.path.expanduser(output_path))
        elif dest_dir is not None:
            fn = overview_filename
            base, ext = os.path.splitext(fn)
            target_path = Path(os.path.expanduser(dest_dir)) / f"{base}_updated_single_page{ext or '.xml'}"
        else:
            target_path = overview_path
        if target_path.parent and not target_path.parent.exists():
            target_path.parent.mkdir(parents=True, exist_ok=True)
        agg_notes = _aggregate_notes(input_dir, overview_filename)
        # Remove old note sections before adding updated ones
        _remove_existing_notes(root)
        # Use FM box (bottom one) as anchor for notes
        _add_notes_to_overview(root, fm_geo, agg_notes)
        _set_single_page(root)
        wrapper = _wrap_mxfile(root, "Workday Overview Updated")
        ET.ElementTree(wrapper).write(str(target_path), encoding="utf-8", xml_declaration=False)
    return added_total


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir", required=True)
    p.add_argument("--overview", required=True)
    p.add_argument("--output-path", required=False)
    p.add_argument("--create-new", action="store_true")
    p.add_argument("--dest-dir", required=False)
    args = p.parse_args()
    if args.create_new:
        default_out = Path(os.path.expanduser(args.dest_dir or "~/Downloads")) / "Workday_Overview_new_single_page.xml"
        count = create_overview(args.input_dir, args.output_path or str(default_out))
        print(f"Created overview with {count} integrations")
    else:
        added = update_overview(args.input_dir, args.overview, args.output_path, args.dest_dir)
        print(f"Added {added} integrations")


if __name__ == "__main__":
    main()
