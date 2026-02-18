DROP TABLE IF EXISTS ref_country_phone_format
;
CREATE TABLE ref_country_phone_format
    AS
WITH src_phone_format
     AS (
SELECT
       TRIM(country)                                AS country_name
     , TRIM("International Phone Code")             AS international_phone_code_raw
     , TRIM("Area Code Validation Message")         AS area_code_msg
     , TRIM("Phone Number Validation Message")      AS phone_number_msg
     , TRIM("Mobile Area Code Message")             AS mobile_area_code_msg
     , TRIM("Mobile Phone Number Message")          AS mobile_phone_number_msg
  FROM stg_fin_phone_number_format
       )
   , parsed
     AS (
SELECT
       s.country_name                                                     AS country_name
     , REGEXP_EXTRACT(
           s.international_phone_code_raw
         , '([0-9]+)'
         , 1
       )                                                                  AS international_phone_code_digits
     , CAST(
           COALESCE(
               REGEXP_EXTRACT(s.area_code_msg, '([0-9]+)-([0-9]+) digits', 1)
             , REGEXP_EXTRACT(s.area_code_msg, '([0-9]+) digits', 1)
           )
           AS INTEGER
       )                                                                  AS landline_area_min_digits
     , CAST(
           COALESCE(
               REGEXP_EXTRACT(s.area_code_msg, '([0-9]+)-([0-9]+) digits', 2)
             , REGEXP_EXTRACT(s.area_code_msg, '([0-9]+) digits', 1)
           )
           AS INTEGER
       )                                                                  AS landline_area_max_digits
     , CASE
         WHEN s.area_code_msg ILIKE '%may be preceded by ''0''%'
         THEN TRUE
         ELSE FALSE
       END                                                                AS landline_area_trunk_zero
     , CAST(
           COALESCE(
               REGEXP_EXTRACT(s.phone_number_msg, '([0-9]+)-([0-9]+) digits', 1)
             , REGEXP_EXTRACT(s.phone_number_msg, '([0-9]+) digits', 1)
           )
           AS INTEGER
       )                                                                  AS landline_phone_min_digits
     , CAST(
           COALESCE(
               REGEXP_EXTRACT(s.phone_number_msg, '([0-9]+)-([0-9]+) digits', 2)
             , REGEXP_EXTRACT(s.phone_number_msg, '([0-9]+) digits', 1)
           )
           AS INTEGER
       )                                                                  AS landline_phone_max_digits
     , CAST(
           COALESCE(
               REGEXP_EXTRACT(s.mobile_area_code_msg, '([0-9]+)-([0-9]+) digits', 1)
             , REGEXP_EXTRACT(s.mobile_area_code_msg, '([0-9]+) digits', 1)
           )
           AS INTEGER
       )                                                                  AS mobile_area_min_digits
     , CAST(
           COALESCE(
               REGEXP_EXTRACT(s.mobile_area_code_msg, '([0-9]+)-([0-9]+) digits', 2)
             , REGEXP_EXTRACT(s.mobile_area_code_msg, '([0-9]+) digits', 1)
           )
           AS INTEGER
       )                                                                  AS mobile_area_max_digits
     , CASE
         WHEN s.mobile_area_code_msg ILIKE '%may be preceded by ''0''%'
         THEN TRUE
         ELSE FALSE
       END                                                                AS mobile_area_trunk_zero
     , CAST(
           COALESCE(
               REGEXP_EXTRACT(s.mobile_phone_number_msg, '([0-9]+)-([0-9]+) digits', 1)
             , REGEXP_EXTRACT(s.mobile_phone_number_msg, '([0-9]+) digits', 1)
           )
           AS INTEGER
       )                                                                  AS mobile_phone_min_digits
     , CAST(
           COALESCE(
               REGEXP_EXTRACT(s.mobile_phone_number_msg, '([0-9]+)-([0-9]+) digits', 2)
             , REGEXP_EXTRACT(s.mobile_phone_number_msg, '([0-9]+) digits', 1)
           )
           AS INTEGER
       )                                                                  AS mobile_phone_max_digits
  FROM src_phone_format s
       )
SELECT
       c.country_code                                                     AS country_code
     , p.country_name                                                     AS country_name
     , d.device_type                                                      AS device_type
     , p.international_phone_code_digits                                  AS international_phone_code_digits
     , CASE d.device_type
         WHEN 'Landline' THEN p.landline_area_min_digits
         WHEN 'Mobile'   THEN p.mobile_area_min_digits
         WHEN 'Fax'      THEN p.landline_area_min_digits
       END                                                                AS area_min_digits
     , CASE d.device_type
         WHEN 'Landline' THEN p.landline_area_max_digits
         WHEN 'Mobile'   THEN p.mobile_area_max_digits
         WHEN 'Fax'      THEN p.landline_area_max_digits
       END                                                                AS area_max_digits
     , CASE d.device_type
         WHEN 'Landline' THEN p.landline_area_trunk_zero
         WHEN 'Mobile'   THEN p.mobile_area_trunk_zero
         WHEN 'Fax'      THEN p.landline_area_trunk_zero
       END                                                                AS area_trunk_zero
     , CASE d.device_type
         WHEN 'Landline' THEN p.landline_phone_min_digits
         WHEN 'Mobile'   THEN p.mobile_phone_min_digits
         WHEN 'Fax'      THEN p.landline_phone_min_digits
       END                                                                AS phone_min_digits
     , CASE d.device_type
         WHEN 'Landline' THEN p.landline_phone_max_digits
         WHEN 'Mobile'   THEN p.mobile_phone_max_digits
         WHEN 'Fax'      THEN p.landline_phone_max_digits
       END                                                                AS phone_max_digits
  FROM parsed p
 CROSS JOIN (VALUES ('Landline'), ('Mobile'), ('Fax')) d(device_type)
       LEFT OUTER JOIN ref_country c
                    ON UPPER(c.country_name) = UPPER(p.country_name)
;
