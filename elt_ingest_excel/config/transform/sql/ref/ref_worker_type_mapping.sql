DROP TABLE IF EXISTS ref_worker_type_mapping
;
CREATE TABLE ref_worker_type_mapping
    AS
SELECT
       TRIM(source_column) source_column
     , TRIM(source_value)  source_value
     , TRIM(target_value)  target_value
  FROM read_json_auto(
           '/Users/rpatel/Documents/__code/git/emailrak/elt_lake/elt_ingest_excel/config/data/ref_worker_type_mapping.json'
       )
;
