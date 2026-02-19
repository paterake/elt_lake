DROP TABLE IF EXISTS ref_country_county_state_town_mapping
;
CREATE TABLE ref_country_county_state_town_mapping
    AS
SELECT
       TRIM(country_code)      AS country_code
     , TRIM(town_city_name)    AS town_city_name
     , TRIM(county_state_name) AS county_state_name
  FROM read_json_auto(
           '/Users/rpatel/Documents/__code/git/emailrak/elt_lake/elt_ingest_excel/config/data/ref_country_county_state_town_mapping.json'
       )
;
