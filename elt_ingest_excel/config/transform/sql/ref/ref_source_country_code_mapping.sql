DROP TABLE IF EXISTS ref_source_country_code_mapping
;
CREATE TABLE ref_source_country_code_mapping
    AS
SELECT
       TRIM(source_country_code)          source_country_code
     , TRIM(country_code)                 country_code
  FROM read_json_auto(
           '/Users/rpatel/Documents/__code/git/emailrak/elt_lake/elt_ingest_excel/config/data/ref_source_country_code_mapping.json'
       )
;
