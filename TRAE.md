# SQL Formatting Rules (Trae)

- Use leading commas in SELECT lists, JOIN lists, and ORDER BY
- Keep commas inline (not leading) inside function argument lists
- One column/expression per line; align aliases to a clean column
- Prefer implied aliases (no `AS`) for columns and tables
- Uppercase SQL keywords; keep identifiers as they come
- Always alias tables and prefix columns with the alias
- Align major clauses vertically for easy eye tracing
- Format CTEs with leading commas and consistent indentation

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
          ON b.id                            = a.ref_id
 WHERE a.active                              = TRUE
;
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
       (PARTITION BY t.nrm_vendor_name
            ORDER BY
              t.created_date                  ASC  NULLS LAST
            , CASE
                WHEN t.last_payment_date > TIMESTAMP '1900-01-01'
                THEN t.last_payment_date
                ELSE NULL
              END                             DESC NULLS LAST
       )                                      rnk
  FROM cte_base                               t
       )
SELECT
       t.*
  FROM cte_ranked                             t
 WHERE t.rnk                                  = 1
;
```

## Function Arguments

- Inside function calls, keep commas inline:

```sql
TRIM(BOTH ' ' FROM COALESCE(t.col_one, 'default'))
```

## General Notes

- Prefer deterministic ordering for generators
- Keep indentation consistent; align ON predicates and AND/OR conditions
- End statements with a semicolon
