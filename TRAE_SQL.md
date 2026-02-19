# SQL Formatting Rules (Trae)

- Use leading commas in SELECT lists, JOIN lists, and ORDER BY
- Keep commas inline (not leading) inside function argument lists
- One column/expression per line; align aliases to a clean column
- Prefer implied aliases (no `AS`) for columns and tables
- Uppercase SQL keywords; keep identifiers as they come
- Always alias tables and prefix columns with the alias
- Align major clauses vertically for easy eye tracing
- Format CTEs with leading commas and consistent indentation
 - Alias column rules for SELECT (see below)

## SELECT Example

```sql
SELECT
       t.column_one                         alias_one
     , t.column_two                         alias_two
     , TRIM(LOWER(t.column_three))          alias_three
  FROM some_table                           t
 WHERE t.filter_col                         = 'value'
   AND t.other_col                          IS NOT NULL
 ORDER BY
       t.created_date                       ASC  NULLS LAST
     , t.last_payment_date                  DESC NULLS LAST
;
```

## JOIN Example

```sql
SELECT
       a.id                                  id
     , a.name                                name
     , b.code                                status_code
  FROM main_table                            a
       INNER JOIN
       ref_table                             b
         ON  b.id                            = a.ref_id
 WHERE a.active                              = TRUE
;
```

## Window / Parentheses Alignment

- If the opening parenthesis is on a new line, align it under the start of the function keyword; the closing parenthesis aligns to the same column.
- If the opening parenthesis is on the same line as the function, indent contents consistently and place the closing parenthesis at that indentation level.
- Use leading commas for each item after multi-line expressions.

Example (new-line parens):

```sql
ROW_NUMBER() OVER
              (
                 PARTITION BY t.group_key
                   ORDER BY
                      CASE
                        WHEN t.flag = 1 THEN 0
                        ELSE 1
                      END ASC
                    , t.created_date ASC  NULLS LAST
              )                             rnk
```

## CTE Example

```sql
WITH cte_base
  AS (
SELECT
       t.id                                   id
     , TRIM(t.vendor_name)                    nrm_vendor_name
  FROM vendors                                t
       )
    , cte_ranked
  AS (
SELECT t.*
     , ROW_NUMBER() OVER
                     (
                        PARTITION BY t.nrm_vendor_name
                          ORDER BY
                             t.created_date                  ASC  NULLS LAST
                           , CASE
                                WHEN t.last_payment_date > TIMESTAMP '1900-01-01'
                                THEN t.last_payment_date
                                ELSE NULL
                             END                             DESC NULLS LAST
                     )                       rnk
  FROM cte_base                               t
       )
SELECT
       t.*
  FROM cte_ranked                             t
 WHERE t.rnk                                  = 1
;
```

## Simple UNION ALL (Exception)

For initial staging where multiple identically shaped sources are unioned without complex expressions:

- Use one SELECT per line with inline commas and compact formatting.
- Always alias the table and use the alias for `*` (e.g., `t.*`).
- Keep literal tags (e.g., business_unit) inline before `t.*` when needed.
- No leading commas in these compact SELECTs.
- Align the first column alias (e.g., `business_unit`) to a shared column by padding spaces after differing literal lengths (e.g., 'FA', 'NFC', 'WNSL').
- Align the table alias to a shared column by padding spaces after the table name so all `t` aliases start at the same column.

Examples:

```sql
-- Direct unions
SELECT t.* FROM table1 t
UNION ALL
SELECT t.* FROM table2 t
;
```

```sql
-- Light transform with a literal label
SELECT 'A' unit, t.* FROM table1 t
UNION ALL
SELECT 'B' unit, t.* FROM table2 t
;
```

```sql
-- Aligned staging unions (example of padded alignment)
SELECT 'FA'   business_unit, t.* FROM fin_supplier_creditor_created_date_fa            t
UNION ALL
SELECT 'FA'   business_unit, t.* FROM fin_supplier_creditor_last_payment_date_fa       t
UNION ALL
SELECT 'FA'   business_unit, t.* FROM fin_supplier_creditor_last_purchase_date_fa      t
UNION ALL
SELECT 'NFC'  business_unit, t.* FROM fin_supplier_creditor_created_date_nfc           t
UNION ALL
SELECT 'NFC'  business_unit, t.* FROM fin_supplier_creditor_last_payment_date_nfc      t
UNION ALL
SELECT 'NFC'  business_unit, t.* FROM fin_supplier_creditor_last_purchase_date_nfc     t
UNION ALL
SELECT 'WNSL' business_unit, t.* FROM fin_supplier_creditor_created_date_wnsl          t
UNION ALL
SELECT 'WNSL' business_unit, t.* FROM fin_supplier_creditor_last_payment_date_wnsl     t
UNION ALL
SELECT 'WNSL' business_unit, t.* FROM fin_supplier_creditor_last_purchase_date_wnsl    t
```

## Function Arguments

- Inside function calls, keep commas inline:

```sql
TRIM(BOTH ' ' FROM COALESCE(t.col_one, 'default'))
```

## Multi‑Line Expressions and Separators

- When a multi-line expression (e.g., CASE, nested function) appears in an ORDER BY/SELECT list:
  - Place the separator comma at the start of the next line (leading comma).
  - Do not trail a comma at the end of the multi-line block.
  - In CASE blocks, place THEN on a new line aligned under WHEN; place ELSE on its own line aligned with WHEN/THEN for vertical scanning.

Example:

```sql
ORDER BY
      CASE
        WHEN t.last_payment_date  > TIMESTAMP '1900-01-01'
         OR t.last_purchase_date > TIMESTAMP '1900-01-01'
        THEN 0
        ELSE 1
      END ASC
    , t.created_date ASC  NULLS LAST
    , CASE
        WHEN t.last_payment_date > TIMESTAMP '1900-01-01'
        THEN t.last_payment_date
        ELSE NULL
      END DESC NULLS LAST
;
```

## Alignment Columns (3‑Space Tabs)

- Assume a tab stop width of 3 spaces for visual alignment.
- Within a logical block (e.g., a CTE or the final SELECT):
  - Align the table alias column in FROM/JOIN lines to a common stop.
  - Ensure all aliases (e.g., `t`, `bu`) start in the same column across FROM and JOIN lines.
  - Align ON predicates so the `=` operator forms a vertical column across related lines; pad spaces after the left-hand side to hit the shared `=` column.
  - Align SELECT aliases to a consistent column (rules below).
- Exception: If a left-hand expression is significantly longer than the rest, do not over‑pad; keep a single space before the alias or operator instead of breaking the layout.

Example (3‑space stops for FROM/JOIN alias and ON `=`):

```sql
SELECT
       s.supplier_id                                   supplier_id
     , s.nrm_vendor_name                               supplier_name
  FROM src_fin_supplier                                  s
       LEFT JOIN
       ref_supplier_category_mapping                      m
         ON  UPPER(TRIM(s.vendor_class_id))             = m.source_supplier_category
;
```

## Human‑Scan Principles

- Vertical anchors: Keep SELECT/FROM/JOIN/WHERE/ORDER BY keywords in consistent columns to reduce left‑right jitter when scanning up/down.
- Alias columns: Choose a target column for SELECT aliases and stick to it across the file; allow a short exception when the left side would cause excessive padding.
- Table aliases: Ensure FROM/JOIN aliases start at the same column; this makes the join chain easy to follow top‑to‑bottom and bottom‑to‑top.
- Predicates: Line up the `=` in ON conditions to a shared column for quick visual diffing of join keys.
- Multi‑line blocks: For CASE/OVER or nested functions, align open/close parentheses to the function keyword column; use leading commas for following items.
- Staging unions: When using the compact UNION ALL style, align the first column alias (e.g., `business_unit`) and the table alias `t` via padding so each arm reads as a visual column.

### Quick Checklist

- Keywords vertically aligned
- Leading commas for lists; inline commas for function args
- 3‑space tab visual alignment within each block
- Table/column aliases aligned to shared columns
- `=` in ON predicates vertically aligned
- Parentheses aligned under the function keyword (if on a new line)

## SELECT Alias Column Rules

- Minimum alias start column is 40 (absolute column from line start).
- Determine the alias column within a SELECT list by:
  - Find the longest single‑line projection expression in that list.
  - Set the alias column to the next 3‑space tab stop past the end of that expression.
  - If that position is less than column 40, set the alias column to exactly column 40 (do NOT advance to a later tab stop).
- For projections whose expression end would place the alias beyond column 70:
  - Place the alias on the next line, starting at the same alias column chosen for the list.
  - Multi‑line expressions use the alias after the final token if the end column ≤ 70; otherwise, put the alias on the next line, aligned to the list’s alias column.
- Always keep one space between the alias column and the alias itself (after padding to the column).

Example (single‑line longest expression sets the alias column):

```sql
SELECT
       TRIM(col_one)                                  col_one
     , COALESCE(NULLIF(TRIM(col_two), ''), '0')       col_two
     , LOWER(col_three)                               col_three
```

Example (multi‑line with alias pushed to next line due to >70 column):

```sql
SELECT
       CASE
         WHEN long_expression_part_one  = 1
          AND long_expression_part_two  = 2
         THEN 'X'
         ELSE 'Y'
       END                                            case_result
     , very_very_very_very_very_very_very_very_very_very_long_function_name(col)
                                                     long_fn_alias
;
```
