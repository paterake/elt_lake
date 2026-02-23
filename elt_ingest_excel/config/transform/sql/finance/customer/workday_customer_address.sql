DROP TABLE IF EXISTS workday_customer_address
;
CREATE TABLE workday_customer_address
    AS
WITH base AS (
  SELECT
         c.customer_id                                                          customer_id
       , c.nrm_customer_name                                                    customer_name
       , TRIM(c.customer_id) || '_' || COALESCE(TRIM(c.address_code), 'MAIN')   address_id
       , c.nrm_country_name                                                     country
       , c.nrm_country_code                                                     country_code
       , rx.instance                                                            region
       , CASE
          WHEN r0.city                IS NOT NULL
          THEN r0.city
          WHEN r3.town_city_name      IS NOT NULL
          THEN r3.town_city_name
          WHEN r4.town_city_name      IS NOT NULL
          THEN r4.town_city_name
          ELSE NULLIF(TRIM(c.city), '')
         END                                                                    city_pre
       , COALESCE(
           NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(c.address_1, '[\"`<>|;]', '', 'g'), '[{}]', '', 'g')), '')
         , NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(c.address_2, '[\"`<>|;]', '', 'g'), '[{}]', '', 'g')), '')
         , NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(c.address_3, '[\"`<>|;]', '', 'g'), '[{}]', '', 'g')), '')
         )                                                                      address_line_1_pre
       , NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(c.address_2, '[\"`<>|;]', '', 'g'), '[{}]', '', 'g')), '')
                                                                                address_line_2_pre
       , NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(c.address_3, '[\"`<>|;]', '', 'g'), '[{}]', '', 'g')), '')
                                                                                address_line_3_pre
       , TRIM(UPPER(c.post_code))                                               postal_code
    FROM src_fin_customer                         c
         LEFT OUTER JOIN
         ref_post_code_county                     r0
            ON UPPER(TRIM(c.post_code))           LIKE r0.postcode || ' %' 
         LEFT OUTER JOIN 
         ref_workday_country_state_region         r1
           ON r1.country                          = c.nrm_country_name
          AND UPPER(TRIM(r1.instance))            = UPPER(TRIM(c.county))
         LEFT OUTER JOIN 
         ref_workday_country_state_region         r2
           ON r2.country                          = c.nrm_country_name
          AND UPPER(TRIM(r2.instance))            = UPPER(TRIM(c.city))   
         LEFT OUTER JOIN
         ref_country_county_state_town_mapping    r3
           ON r3.country_code                     = c.nrm_country_code
          AND UPPER(TRIM(r3.town_city_name))      = UPPER(TRIM(c.county))
         LEFT OUTER JOIN
         ref_country_county_state_town_mapping    r4
           ON r4.country_code                     = c.nrm_country_code
          AND UPPER(TRIM(r4.town_city_name))      = UPPER(TRIM(c.city))       
         LEFT OUTER JOIN 
         ref_workday_country_state_region         rx
           ON rx.country                          = c.nrm_country_name
          AND UPPER(TRIM(rx.instance))            = CASE
                                                     WHEN r0.county             IS NOT NULL THEN UPPER(TRIM(r0.county))
                                                     WHEN r1.instance           IS NOT NULL THEN UPPER(TRIM(r1.instance))
                                                     WHEN r2.instance           IS NOT NULL THEN UPPER(TRIM(r2.instance)) 
                                                     WHEN r3.county_state_name  IS NOT NULL THEN UPPER(TRIM(r3.county_state_name))
                                                     WHEN r4.county_state_name  IS NOT NULL THEN UPPER(TRIM(r4.county_state_name))
                                                     ELSE NULLIF(UPPER(TRIM(c.county)), '')
                                                    END
   WHERE COALESCE(NULLIF(TRIM(c.address_1), ''), NULLIF(TRIM(c.address_2), ''), NULLIF(TRIM(c.address_3), '')) IS NOT NULL
     AND NULLIF(TRIM(c.address_1), '') NOT IN ('[Not Known]') 
),
norm AS (
  SELECT
         b.*
       , udf_normalize_address(
           b.address_line_1_pre,
           b.address_line_2_pre,
           b.address_line_3_pre,
           NULL,
           b.city_pre,
           b.region,
           b.postal_code,
           b.country_code
         ) AS norm
    FROM base b
)
SELECT
       n.customer_id                                                          customer_id
     , n.customer_name                                                        customer_name
     , NULL                                                                   formatted_address
     , NULL                                                                   address_format_type
     , NULL                                                                   defaulted_business_site_address
     , NULL                                                                   delete_flag
     , NULL                                                                   do_not_replace_all
     , NULL                                                                   last_modified
     , NULL                                                                   descriptor
     , n.address_id                                                           address_id
     , n.country                                                              country
     , COALESCE(n.norm.country_code, n.country_code)                           country_code
     , COALESCE(n.norm.region, n.region)                                       region
     , NULL                                                                   subregion
     , COALESCE(n.norm.city, TRIM(REGEXP_REPLACE(REGEXP_REPLACE(n.city_pre, '[\"`<>|;]', '', 'g'), '\\s+', ' ', 'g'))) city
     , NULL                                                                   submunicipality
     , n.norm.address_line_1                                                  address_line_1
     , n.norm.address_line_2                                                  address_line_2
     , n.norm.address_line_3                                                  address_line_3
     , NULL                                                                   address_line_4
     , COALESCE(n.norm.postal_code, n.postal_code)                             postal_code
     , 'Yes'                                                                  is_public
     , 'Yes'                                                                  is_primary
     , NULL                                                                   address_type   
     , NULL                                                                   effective_date
     , NULL                                                                   use_for
     , NULL                                                                   use_for_tenanted
     , NULL                                                                   customer_comment
     , NULL                                                                   number_of_days
     , NULL                                                                   municipality_local
     , NULL                                                                   optional_address
  FROM norm n
;
