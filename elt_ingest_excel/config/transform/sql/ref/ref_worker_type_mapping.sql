DROP TABLE IF EXISTS ref_worker_type_mapping
;
-- Maps Okta user_type and department_1 values to canonical worker types
-- Rules:
--   • 'Supplier Staff' = Default for all external/human workers (no source evidence for sole traders exists)
--   • NULL = Non-human identities or values requiring exclusion from staff-type classification
--   • 'Sole Trader Staff' = Not used (requires explicit contract/tax evidence not present in source data)
CREATE TABLE ref_worker_type_mapping
    AS
SELECT
       TRIM(source_column) AS source_column
     , TRIM(source_value)  AS source_value
     , TRIM(target_value)  AS target_value
  FROM read_json_auto(
           '/Users/rpatel/Documents/__code/git/emailrak/elt_lake/elt_ingest_excel/config/data/ref_worker_type_mapping.json'
       )
;
