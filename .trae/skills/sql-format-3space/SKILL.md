---
name: "sql-format-3space"
description: "Formats SQL per TRAE.md rules (3‑space tabs, leading commas, alias/JOIN/ON alignment, CASE layout). Invoke when asked to format SQL to house style."
---

# SQL Formatter (TRAE.md Rules - Canonicalized)

Canonical source of truth

- All SQL formatting rules are defined once in the repository root at:
  - TRAE.md → “SQL Formatting Rules (Trae)”
- This skill does not duplicate the rule text; it enforces the rules exactly as documented in TRAE.md.
- Update TRAE.md to change the house style; this skill will follow that specification.

What this skill does (enforcement summary)

- Applies the Trae SQL formatting rules from TRAE.md.
- Aligns:
  - SELECT aliases to a shared column
  - FROM/JOIN table aliases to a shared column
  - ON predicate `=` signs to a shared column
  - THEN/ELSE on their own lines within CASE blocks
- Uses leading commas for SELECT/JOIN/ORDER BY lists; inline commas inside function arg lists.
- Uppercases SQL keywords and prefers implied aliases (no AS) for columns/tables.
- Follows CTE/window function alignment as specified in TRAE.md.

When to invoke

- The user asks to “format SQL”, “align aliases”, “fix JOIN alignment”, “apply 3‑space tabs”, or similar.
- Before committing SQL-heavy changes to ensure consistency with house style.

Reference

- See repository rules: TRAE.md → “SQL Formatting Rules (Trae)”
- That document includes full examples for SELECT, JOIN, CTEs, window functions, and exceptions (e.g., compact UNION ALL).

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

- TRAE.md is the source of truth. This skill enforces those rules and defers to TRAE.md for details.
- Apply by editing SQL to match; use this skill before merging SQL‑heavy changes.
- For bulk changes across files, invoke the skill and then request formatting for the target list.
