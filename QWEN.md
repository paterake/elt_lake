# SQL Formatting Rules

- Each column in a SELECT statement goes on its own line
- Use leading commas (`, column_name` style)
- Column aliases aligned to a consistent right-hand position
- No `AS` keyword before column aliases (alias is implied)
- Keywords (SELECT, FROM, WHERE, etc.) aligned consistently
- Always alias tables and prefix column names with the table alias
- Example:

```sql
SELECT t.column_one                    alias_one
     , t.column_two                    alias_two
     , TRIM(LOWER(t.column_three))     alias_three
  FROM table_name                      t
 WHERE t.condition                     = 'value'
```
