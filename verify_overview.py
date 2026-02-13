
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path

def get_int_ids(root):
    ids = set()
    # Check FactSheets
    for obj in root.findall(".//object"):
        if obj.get("type") == "factSheet":
            label = obj.get("label", "")
            # Look for INTxxx in label
            matches = re.findall(r"INT\d{3}", label)
            ids.update(matches)
    
    # Check Edges/Connectors (sometimes labeled) or UserObjects (notes) if needed, 
    # but for verification of "integrations", the boxes are key.
    # The previous script also looked at user objects for INTs, let's do that to be safe.
    for uo in root.findall(".//UserObject"):
        label = uo.get("label", "")
        matches = re.findall(r"INT\d{3}", label)
        ids.update(matches)
        
    return ids

def get_factsheets(root):
    """Returns a set of (factSheetId, label, type) tuples."""
    fs = set()
    for obj in root.findall(".//object"):
        if obj.get("type") == "factSheet":
            fid = obj.get("factSheetId")
            # We clean the label to avoid minor whitespace issues or INT prefixes added during generation affecting match
            # But the user asked if assets are captured "as is". 
            # The updater adds "\nINTxxx" to vendor labels. We should handle that.
            raw_label = obj.get("label", "")
            # Remove the appended INT code for comparison if it exists
            clean_label = re.sub(r"\nINT\d{3}", "", raw_label).strip()
            
            # Note: The updater might NOT put the INT ID in the label if it was already there?
            # actually checking the code: f"{vendor['label']}\n{int_id}"
            
            ftype = obj.get("factSheetType")
            if fid: # Only track if it has an ID
                fs.add((fid, clean_label, ftype))
    return fs

def verify():
    downloads = Path(os.path.expanduser("~/Downloads/leanix_workday_int"))
    new_overview_path = Path("Workday_Overview_New.xml")
    original_overview_path = downloads / "COR_V00.01_INT000_Workday_Overview.xml"
    
    print(f"Verifying New Overview: {new_overview_path.name}")
    
    if not new_overview_path.exists():
        print("Error: New overview file not found!")
        return

    # 1. Load New Overview
    try:
        new_tree = ET.parse(new_overview_path)
        new_root = new_tree.getroot()
        # Handle mxfile wrapper if present
        if new_root.tag == "mxfile":
            new_root = new_root.find(".//diagram").find(".//mxGraphModel") # simplified, might need decoding if compressed, but script writes raw xml
            # If the script wrote it as nested XML inside diagram, it should be accessible.
            # The script uses _wrap_mxfile which appends root directly.
            if new_root is None:
                 # It might be directly under diagram if not compressed
                 new_root = new_tree.find(".//diagram").find(".//mxGraphModel")
                 if new_root is None:
                     # Maybe it's just the root if not wrapped correctly or different structure
                     new_root = new_tree.getroot()
    except Exception as e:
        print(f"Failed to parse new overview: {e}")
        return

    new_ints = get_int_ids(new_root)
    new_fs = get_factsheets(new_root)
    new_fs_ids = {f[0] for f in new_fs}
    
    print(f"Found {len(new_ints)} integrations in New Overview: {sorted(new_ints)}")
    
    # 2. Verify Original Overview Content
    print("\n--- Verifying Original Overview Preservation ---")
    orig_tree = ET.parse(original_overview_path)
    orig_root = orig_tree.getroot()
    orig_ints = get_int_ids(orig_root)
    orig_fs = get_factsheets(orig_root)
    
    missing_orig_ints = orig_ints - new_ints
    if missing_orig_ints:
        print(f"[FAIL] Missing integrations from Original Overview: {missing_orig_ints}")
    else:
        print(f"[PASS] All {len(orig_ints)} integrations from Original Overview are present.")

    # Check FactSheets (Assets)
    # We check if IDs match. Labels might have changed slightly (added INT ids), so we rely on IDs.
    missing_orig_fs = []
    for fid, lbl, ftype in orig_fs:
        if fid not in new_fs_ids:
            missing_orig_fs.append((fid, lbl))
    
    if missing_orig_fs:
        print(f"[FAIL] Missing FactSheets from Original Overview: {missing_orig_fs}")
    else:
        print(f"[PASS] All {len(orig_fs)} FactSheets from Original Overview are present.")

    # 3. Verify Other Integration Files
    print("\n--- Verifying Individual Integration Files ---")
    all_files = list(downloads.glob("COR_V00.01_INT*.xml"))
    for xml_file in all_files:
        if xml_file.name == original_overview_path.name:
            continue
            
        tree = ET.parse(xml_file)
        root = tree.getroot()
        file_ints = get_int_ids(root)
        file_fs = get_factsheets(root)
        
        # Check Integrations
        file_missing_ints = file_ints - new_ints
        if file_missing_ints:
            print(f"[FAIL] {xml_file.name}: Missing integration IDs {file_missing_ints}")
        else:
            # print(f"[PASS] {xml_file.name}: Integrations found.")
            pass
            
        # Check Assets
        # Note: The overview script filters out some objects (like inventory items not being used?). 
        # But user asked if assets are captured. 
        # The script extracts Vendor, Intermediary, and Workday.
        file_missing_fs = []
        for fid, lbl, ftype in file_fs:
            if fid not in new_fs_ids:
                # Ignore if it's the Workday box itself, as that is merged/centralized
                if "Workday" in lbl: 
                    continue
                file_missing_fs.append((fid, lbl))
        
        if file_missing_fs:
            print(f"[FAIL] {xml_file.name}: Missing assets (FactSheets):")
            for item in file_missing_fs:
                print(f"  - {item}")
        else:
            print(f"[PASS] {xml_file.name}: All relevant assets found.")

if __name__ == "__main__":
    verify()
