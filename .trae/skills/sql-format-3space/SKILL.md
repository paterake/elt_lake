---
name: "sql-format-3space"
description: "Formats SQL per TRAE.md rules (3‑space tabs, leading commas, alias/JOIN/ON alignment, CASE layout). Invoke when asked to format SQL to house style."
---

# SQL Formatter (TRAE.md Rules)

What this skill does

- Applies the full Trae SQL formatting rules defined in TRAE.md.
- Aligns:
  - SELECT aliases to a shared column
  - FROM/JOIN table aliases to a shared column
  - ON predicate `=` signs to a shared column
  - THEN/ELSE on their own lines within CASE blocks
- Uses leading commas for SELECT/JOIN/ORDER BY lists; inline commas inside function arg lists.
- Uppercases SQL keywords and prefers implied aliases (no AS) for columns/tables.
- Follows CTE and window function alignment as specified in TRAE.md.

When to invoke

- The user asks to “format SQL”, “align aliases”, “fix JOIN alignment”, “apply 3‑space tabs”, or similar.
- Before committing SQL-heavy changes to ensure consistency with house style.

Guidelines (Essentials, from TRAE.md)

- Keywords in consistent columns; one expression per line.
- SELECT aliases: pick a target column and align visually using 3‑space stops.
- FROM/JOIN aliases: start in the same column; indent JOIN keyword under FROM’s starting column.
- ON predicates: pad so `=` lines up vertically across JOINs.
- CASE blocks: place THEN/ELSE on separate lines aligned under WHEN.
- CTEs: leading comma formatting for subsequent CTEs with consistent indentation.
- Window functions: align opening parenthesis and content per rules.
- Simple UNION ALL exception: compact layout permitted as per TRAE.md.

Examples

```sql
SELECT
       s.supplier_id                                   supplier_id
     , s.nrm_vendor_name                               supplier_name
     , COALESCE(m.supplier_category, 'Services')       supplier_category
  FROM src_fin_supplier                                  s
       LEFT JOIN
       ref_supplier_category_mapping                      m
         ON  UPPER(TRIM(s.vendor_class_id))             = m.source_supplier_category
;
```

Operational Notes

- TRAE.md is the source of truth. This skill summarizes and enforces those rules.
- Apply by editing SQL to match; use this skill before merging SQL‑heavy changes.
- For bulk changes across files, invoke the skill and then request formatting for the target list.
