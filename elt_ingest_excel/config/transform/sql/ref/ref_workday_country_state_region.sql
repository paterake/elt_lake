DROP TABLE IF EXISTS ref_workday_country_state_region
;
CREATE TABLE ref_workday_country_state_region (
    country                            VARCHAR,
    region_type                        VARCHAR,
    instance                           VARCHAR,
    instance_type                      VARCHAR,
    reference_ids                      VARCHAR,
    workday_id                         VARCHAR,
    workbook_value_descriptor          VARCHAR,
    reference_id                       VARCHAR,
);
COPY ref_workday_country_state_region FROM '/Users/rpatel/Documents/__code/git/emailrak/elt_lake/elt_ingest_excel/config/data/ref_workday_country_state_region.csv' (HEADER TRUE, DELIMITER ',')
;
