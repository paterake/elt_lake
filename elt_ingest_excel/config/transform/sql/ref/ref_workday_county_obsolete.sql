DROP TABLE IF EXISTS ref_workday_county_obsolete
;
CREATE TABLE ref_workday_county_obsolete
    AS
SELECT
       TRIM(source_value)                  source_value
     , TRIM(target_value)                  target_value
  FROM read_json_auto(
             '/Users/rpatel/Documents/__code/git/emailrak/elt_lake/elt_ingest_excel/config/data/ref_workday_county_obsolete.json'
       )
;
