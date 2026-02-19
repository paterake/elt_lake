DROP TABLE IF EXISTS ref_source_country_name_mapping
;
CREATE TABLE ref_source_country_name_mapping
    AS
SELECT
       TRIM(source_country_name) AS source_country_name
     , TRIM(country_code)        AS country_code
  FROM read_json_auto(
           '/Users/rpatel/Documents/__code/git/emailrak/elt_lake/elt_ingest_excel/config/data/ref_source_country_name_mapping.json'
       )
;
