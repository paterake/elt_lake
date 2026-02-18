---
name: "excel-column-values"
description: "Extracts Excel column drop-down (Data Validation) or distinct values. Invoke when user asks for column options or unique values from a sheet."
---

# Excel Column Values

Purpose

- Extract the available drop-down values (Data Validation lists) for a specific column in an Excel workbook.
- Alternatively return the distinct, non-blank values present in that column.
- Invoke when the task mentions “Excel drop-down values”, “filter values”, “data validation options”, or “distinct column values”.

Inputs

- workbook_path: absolute or tilde path to .xlsx/.xlsm file
- sheet_name: exact sheet name
- column: column letter (e.g., D) or 1-based index (e.g., 4)
- mode: one of ["auto", "filter", "distinct"] (default: auto)
  - auto: try filter (Data Validation and form controls) first; if unavailable, fallback to distinct values
  - filter: return Data Validation list values if present for the column
  - distinct: return unique non-blank cell values from the column
- Optional: cell or row targeting
  - CELL (e.g., C4) or ROW (e.g., 4) to target a specific cell in the column first. Useful when validation applies only to certain rows.

Execution Guidelines

- Default behavior returns the exact drop-down list when possible (Data Validation or form control). Only if not retrievable does it return distinct cell values, clearly labeled as a fallback.
- Prefer xlwings for Data Validation (filter mode) to capture modern Excel validations that libraries may drop.
- Fallback to openpyxl for:
  - DataValidation ranges on the sheet
  - Resolving named ranges referenced by validations
- On some macOS setups, Excel’s Validation API and Form Controls may not be exposed to automation; in such cases, auto mode falls back to distinct values with an explicit note.
- Always output JSON for machine readability: {sheet, column, mode, count, values}

Python Snippets

- Auto/filter (Data Validation via xlwings, targeted cell first; graceful fallbacks):

```bash
uv run --active python - <<'PY'
import os, json, sys
path = os.path.expanduser(os.environ.get("WB","~/Workbook.xlsx"))
sheet = os.environ.get("SHEET","Sheet1")
col = os.environ.get("COL","D")
cell_arg = os.environ.get("CELL")
row_arg = os.environ.get("ROW")

def xlwings_filter(path, sheet, col):
    try:
        import xlwings as xw
    except Exception:
        return None
    app = None
    vals = set()
    try:
        app = xw.App(visible=False, add_book=False)
        wb = app.books.open(path)
        sht = wb.sheets[sheet]
        # 1) Target a specific cell first if provided
        target_rows = []
        if cell_arg:
            try:
                r = int(''.join(ch for ch in cell_arg if ch.isdigit()))
                target_rows.append(r)
            except Exception:
                pass
        elif row_arg:
            try:
                target_rows.append(int(row_arg))
            except Exception:
                pass
        # 2) Otherwise scan the used range
        if not target_rows:
            used = sht.used_range
            last_row = used.last_cell.row
            end_row = min(last_row, 10000)
            target_rows = list(range(1, end_row+1))
        for r in target_rows:
            cell = sht.range((r, ord(col.upper())-64))
            try:
                v = cell.api.Validation
                t = v.Type
            except Exception:
                continue
            # 3 == xlValidateList
            if t != 3:
                continue
            f = None
            try:
                f = v.Formula1
            except Exception:
                continue
            if not f:
                continue
            ref = f[1:] if isinstance(f, str) and f.startswith('=') else f
            if all(x not in ref for x in ('!', ':')):
                for part in ref.replace(';', ',').split(','):
                    part = part.strip()
                    if part:
                        vals.add(part)
                continue
            try:
                if '!' in ref:
                    sh, rng = ref.split('!', 1)
                    sh = sh.strip(\"'\")
                    rng_obj = wb.sheets[sh].range(rng)
                else:
                    rng_obj = wb.names[ref].refers_to_range
                data = rng_obj.value
                if isinstance(data, list):
                    for row in data:
                        if isinstance(row, list):
                            for x in row:
                                if x not in (None, ''):
                                    vals.add(str(x).strip())
                        else:
                            if row not in (None, ''):
                                vals.add(str(row).strip())
                elif data not in (None, ''):
                    vals.add(str(data).strip())
            except Exception:
                continue
        # Try form control dropdowns near the column if no validations found
        if not vals:
            try:
                api = sht.api
                # Some macOS Excel builds may not expose DropDowns; ignore errors
                dds = api.DropDowns()
                for i in range(1, dds.Count+1):
                    dd = dds.Item(i)
                    try:
                        tl = dd.TopLeftCell
                        if tl.Column != (ord(col.upper())-64):
                            continue
                        lfr = dd.ListFillRange
                        if not lfr:
                            continue
                        if '!' in lfr:
                            sh, rng = lfr.split('!', 1)
                            sh = sh.strip(\"'\")
                            rng_obj = wb.sheets[sh].range(rng)
                        else:
                            rng_obj = wb.names[lfr].refers_to_range
                        data = rng_obj.value
                        if isinstance(data, list):
                            for row in data:
                                if isinstance(row, list):
                                    for x in row:
                                        if x not in (None, ''):
                                            vals.add(str(x).strip())
                                else:
                                    if row not in (None, ''):
                                        vals.add(str(row).strip())
                        elif data not in (None, ''):
                            vals.add(str(data).strip())
                    except Exception:
                        continue
            except Exception:
                pass
    finally:
        try:
            if app is not None:
                app.quit()
        except Exception:
            pass
    return sorted(vals)

def openpyxl_filter(path, sheet, col):
    from openpyxl import load_workbook
    from openpyxl.utils import range_boundaries
    ws = load_workbook(path, data_only=True, keep_vba=True)[sheet]
    col_idx = ord(col.upper())-64
    vals = []
    if ws.data_validations is not None:
        for dv in ws.data_validations.dataValidation:
            if getattr(dv, 'type', None) != 'list':
                continue
            applies = any(cr.min_col <= col_idx <= cr.max_col for cr in dv.ranges)
            if not applies:
                continue
            f1 = dv.formula1
            if not f1:
                continue
            f = f1[1:] if isinstance(f1, str) and f1.startswith('=') else f1
            if isinstance(f, str) and f.startswith('\"') and f.endswith('\"'):
                vals += [x.strip() for x in f.strip('\"').split(',') if x.strip()]
                continue
            wb = ws.parent
            # named range
            if isinstance(f, str) and '!' not in f and f in wb.defined_names:
                dn = wb.defined_names[f]
                for title, area in dn.destinations:
                    ws2 = wb[title]
                    min_c, min_r, max_c, max_r = range_boundaries(area)
                    for row in ws2.iter_rows(min_row=min_r, max_row=max_r, min_col=min_c, max_col=max_c, values_only=True):
                        for cell in row:
                            if cell not in (None, ''):
                                vals.append(str(cell).strip())
                continue
            # sheet!range
            if isinstance(f, str) and '!' in f:
                if f.startswith(\"'\"):  # quoted sheet
                    sh = f.split(\"'\", 2)[1]
                    rng = f.split(\"'\", 2)[2].lstrip('!')
                else:
                    sh, rng = f.split('!', 1)
                ws2 = ws.parent[sh]
                min_c, min_r, max_c, max_r = range_boundaries(rng)
                for row in ws2.iter_rows(min_row=min_r, max_row=max_r, min_col=min_c, max_col=max_c, values_only=True):
                    for cell in row:
                        if cell not in (None, ''):
                            vals.append(str(cell).strip())
    return sorted(set(vals))

vals = xlwings_filter(path, sheet, col)
if vals is None or len(vals) == 0:
    try:
        vals = openpyxl_filter(path, sheet, col)
    except Exception:
        vals = []
mode = os.environ.get("MODE","auto").lower()
out_mode = "filter" if vals else ("distinct" if mode=="auto" else mode)
print(json.dumps({"sheet": sheet, "column": col, "mode": out_mode, "count": len(vals), "values": vals}, ensure_ascii=False))
PY
```

- Distinct (unique values via openpyxl):

```bash
uv run python - <<'PY'
import os, json
from openpyxl import load_workbook

path = os.path.expanduser(os.environ.get("WB","~/Workbook.xlsx"))
sheet = os.environ.get("SHEET","Sheet1")
col = os.environ.get("COL","D")
idx = ord(col.upper())-64 if not col.isdigit() else int(col)

ws = load_workbook(path, data_only=True, read_only=True, keep_vba=True)[sheet]
vals = set()
for row in ws.iter_rows(min_col=idx, max_col=idx, values_only=True):
    v = row[0]
    if v not in (None, ''):
        vals.add(str(v).strip())
vals = sorted(vals)
print(json.dumps({\"sheet\": sheet, \"column\": col, \"mode\": \"distinct\", \"count\": len(vals), \"values\": vals}, ensure_ascii=False))
PY
```

Usage Examples

- Filter values (Data Validation) for D in “Supplier Name”:
  WB=~/Downloads/FIN_Supplier_Workbook_Demo.xlsm SHEET=\"Supplier Name\" COL=D <run the Filter snippet>

- Distinct values for D in “Supplier Name”:
  WB=~/Downloads/FIN_Supplier_Workbook_Demo.xlsm SHEET=\"Supplier Name\" COL=D <run the Distinct snippet>

Notes

- Data Validation in .xlsm files may use newer extensions. The xlwings path provides best coverage on macOS with Excel installed; openpyxl is a fallback.
- If filter returns empty but the sheet shows a drop-down in Excel, use the xlwings snippet and ensure Excel is installed and accessible.

Invocation (Module)

- Preferred invocation using the packaged module:

```bash
uv run --active -m elt_skill_excel_utility \
  --workbook "~/Workbook.xlsx" \
  --sheet "Sheet1" \
  --column D \
  --mode auto
```

- Target a specific cell:

```bash
uv run --active -m elt_skill_excel_utility \
  --workbook "~/Workbook.xlsx" \
  --sheet "Sheet1" \
  --column D \
  --cell D4
```
