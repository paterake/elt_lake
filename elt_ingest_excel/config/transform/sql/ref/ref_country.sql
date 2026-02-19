DROP TABLE IF EXISTS ref_country
;
CREATE TABLE ref_country
    AS
SELECT
       TRIM(country_code)     AS country_code
     , TRIM(language_code)    AS language_code
     , TRIM(currency_code)    AS currency_code
     , TRIM(phone_code)       AS phone_code
     , TRIM(tax_id_type)      AS tax_id_type
     , TRIM(country_name)     AS country_name
  FROM read_json_auto(
           '/Users/rpatel/Documents/__code/git/emailrak/elt_lake/elt_ingest_excel/config/data/ref_country.json'
       )
;
