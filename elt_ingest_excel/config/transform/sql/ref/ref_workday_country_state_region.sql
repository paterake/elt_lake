DROP TABLE IF EXISTS ref_workday_country_state_region
;
CREATE TABLE ref_workday_country_state_region
    AS
SELECT
       TRIM(country)                       country
     , TRIM(region_type)                   region_type
     , TRIM(instance)                      instance
     , TRIM(instance_type)                 instance_type
     , TRIM(reference_ids)                 reference_ids
     , TRIM(workday_id)                    workday_id
     , TRIM(workbook_value_descriptor)     workbook_value_descriptor
     , TRIM(reference_id)                  reference_id
  FROM read_json_auto(
             '/Users/rpatel/Documents/__code/git/emailrak/elt_lake/elt_ingest_excel/config/data/ref_workday_country_state_region.json'
       )
;
