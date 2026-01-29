DROP TABLE IF EXISTS workday_contingent_worker_locations
;
CREATE TABLE workday_contingent_worker_locations
    AS
  WITH cte_locations
    AS (
SELECT DISTINCT
       TRIM(location)                                   location
     , TRIM(county_site)                                county_site
  FROM src_hcm_contingent_worker
 WHERE location IS NOT NULL
   AND TRIM(location) != ''
       )
SELECT
       TRIM(location)                                   location_name
     , NULL                                             location_id
     , 'Business Site'                                  location_usage
     , NULL                                             location_usage_2
     , 'Office'                                         location_type
     , NULL                                             superior_location
     , NULL                                             default_hours_per_week
     , NULL                                             time_zone_reference_id
     , NULL                                             time_zone_descriptor
     , NULL                                             locale
     , 'United Kingdom'                                 country
     , 'GBR'                                            country_code
     , 'GBP'                                            currency_code
     , NULL                                             region
     , NULL                                             subregion
     , NULL                                             city
     , NULL                                             city_subdivision
     , NULL                                             address_line_1
     , NULL                                             address_line_2
     , NULL                                             address_line_3
     , NULL                                             address_line_4
     , NULL                                             postal_code
     , NULL                                             use_for
     , NULL                                             international_phone_code
     , NULL                                             area_code
     , NULL                                             phone_number
     , NULL                                             email_address
     , NULL                                             web_address
     , NULL                                             location_hierarchy_1
     , NULL                                             location_hierarchy_2
     , NULL                                             location_hierarchy_3
     , NULL                                             external_name
     , NULL                                             legacy_location_name
     , NULL                                             location_identifier
     , TRIM(county_site)                                county
     , NULL                                             locality_pay_area
  FROM cte_locations
;
