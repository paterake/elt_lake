DROP TABLE IF EXISTS ref_post_code_county
;
CREATE TABLE ref_post_code_county
    AS
SELECT
       TRIM(postcode)                                postcode
     , CAST(NULLIF(easting  , '') AS INTEGER)        easting
     , CAST(NULLIF(northing , '') AS INTEGER)        northing
     , CAST(NULLIF(latitude , '') AS DOUBLE )        latitude
     , CAST(NULLIF(longitude, '') AS DOUBLE )        longitude
     , TRIM(city)                                    city
     , TRIM(county)                                  county
     , TRIM(country_code)                            country_code
     , TRIM(country_name)                            country_name
     , TRIM(iso3166_2)                               iso3166_2
     , TRIM(region_code)                             region_code
     , TRIM(region_name)                             region_name
  FROM read_json_auto(
           '/Users/rpatel/Documents/__code/git/emailrak/elt_lake/elt_ingest_excel/config/data/ref_post_code_county.json'
       )
;
