DROP TABLE IF EXISTS ref_customer_class
;
CREATE TABLE ref_customer_class
    AS
SELECT
       TRIM(source_value)              source_value
     , TRIM(target_value)              target_value
     , TRIM(notes)                     notes
  FROM read_json_auto(
           '/Users/rpatel/Documents/__code/git/emailrak/elt_lake/elt_ingest_excel/config/data/ref_customer_class.json'
       )
;
