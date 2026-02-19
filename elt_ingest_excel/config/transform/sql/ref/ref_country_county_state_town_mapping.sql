DROP TABLE IF EXISTS ref_country_county_state_town_mapping
;
CREATE TABLE ref_country_county_state_town_mapping
    AS
SELECT
       TRIM(country_code)              country_code
     , TRIM(town_city_name)            town_city_name
     , TRIM(county_state_name)         county_state_name
  FROM read_json_auto(
           '/Users/rpatel/Documents/__code/git/emailrak/elt_lake/elt_ingest_excel/config/data/ref_country_county_state_town_mapping.json'
       )
;
