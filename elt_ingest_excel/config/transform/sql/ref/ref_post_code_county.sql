DROP TABLE IF EXISTS ref_post_code_county
;
CREATE TABLE ref_post_code_county
    AS
SELECT
       TRIM(postcode)                                AS postcode
     , CAST(NULLIF(easting  , '') AS INTEGER)        AS easting
     , CAST(NULLIF(northing , '') AS INTEGER)        AS northing
     , CAST(NULLIF(latitude , '') AS DOUBLE )        AS latitude
     , CAST(NULLIF(longitude, '') AS DOUBLE )        AS longitude
     , TRIM(city)                                    AS city
     , TRIM(county)                                  AS county
     , TRIM(country_code)                            AS country_code
     , TRIM(country_name)                            AS country_name
     , TRIM("iso3166-2")                             AS iso3166_2
     , TRIM(region_code)                             AS region_code
     , TRIM(region_name)                             AS region_name
  FROM read_csv_auto(
           '/Users/rpatel/Documents/__code/git/emailrak/elt_lake/elt_ingest_excel/config/data/ref_post_code_county.csv'
         , header      = TRUE
         , all_varchar = TRUE
       )
;
