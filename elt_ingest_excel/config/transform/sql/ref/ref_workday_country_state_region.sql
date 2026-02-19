DROP TABLE IF EXISTS ref_workday_country_state_region
;
CREATE TABLE ref_workday_country_state_region
    AS
SELECT
       TRIM(country)                       AS country
     , TRIM(region_type)                   AS region_type
     , TRIM(instance)                      AS instance
     , TRIM(instance_type)                 AS instance_type
     , TRIM(reference_ids)                 AS reference_ids
     , TRIM(workday_id)                    AS workday_id
     , TRIM(workbook_value_descriptor)     AS workbook_value_descriptor
     , TRIM(reference_id)                  AS reference_id
  FROM read_json_auto(
             '/Users/rpatel/Documents/__code/git/emailrak/elt_lake/elt_ingest_excel/config/data/ref_workday_country_state_region.json'
       )
;
