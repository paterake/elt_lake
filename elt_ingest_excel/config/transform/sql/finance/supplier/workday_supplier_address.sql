DROP TABLE IF EXISTS workday_supplier_address
;
CREATE TABLE workday_supplier_address 
    AS
SELECT
       s.supplier_id                                                          supplier_id
     , s.nrm_vendor_name                                                      supplier_name
     , NULL                                                                   formatted_address
     , NULL                                                                   address_format_type
     , NULL                                                                   defaulted_business_site_address
     , NULL                                                                   delete_flag
     , NULL                                                                   do_not_replace_all
     , s.created_date                                                         last_modified
     , NULL                                                                   descriptor
     , s.supplier_id || '_' || COALESCE(TRIM(s.vendor_address_code_primary), 'MAIN')
                                                                              address_id
     , s.nrm_country_name                                                     country
     , s.nrm_country_code                                                     country_code
     , rx.instance                                                            region
     , NULL                                                                   subregion
     , CASE
        WHEN r0.city                IS NOT NULL
        THEN r0.city
        WHEN r3.town_city_name      IS NOT NULL
        THEN r3.town_city_name
        WHEN r4.town_city_name      IS NOT NULL
        THEN r4.town_city_name
        ELSE NULLIF(TRIM(s.city), '')
       END                                                                    city
     , NULL                                                                   submunicipality
     , TRIM(REGEXP_REPLACE(REGEXP_REPLACE(s.address_1, '[\"`<>|;{}]', '', 'g'), '\\s+', ' ', 'g'))
                                                                              address_line_1
     , NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(s.address_2, '[\"`<>|;{}]', '', 'g'), '\\s+', ' ', 'g')), '')
                                                                              address_line_2
     , NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(s.address_3, '[\"`<>|;{}]', '', 'g'), '\\s+', ' ', 'g')), '')
                                                                              address_line_3
     , NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(s.addressline_4, '[\"`<>|;{}]', '', 'g'), '\\s+', ' ', 'g')), '')
                                                                              address_line_4
     , TRIM(UPPER(s.post_code))                                               postal_code
     , 'Yes'                                                                  public_flag
     , 'Yes'                                                                  primary_flag
     , NULL                                                                   effective_date
     , NULL                                                                   address_type
     , NULL                                                                   use_for
     , NULL                                                                   use_for_tenanted
     , NULL                                                                   address_comments
     , NULL                                                                   number_of_days
     , NULL                                                                   municipality_local
  FROM src_fin_supplier                         s
       LEFT OUTER JOIN
       ref_post_code_county                     r0
          ON UPPER(TRIM(s.post_code))           LIKE r0.postcode || ' %' 
       LEFT OUTER JOIN 
       ref_workday_country_state_region         r1
         ON r1.country                          = s.nrm_country_name
        AND UPPER(TRIM(r1.instance))            = UPPER(TRIM(s.county))
       LEFT OUTER JOIN 
       ref_workday_country_state_region         r2
         ON r2.country                          = s.nrm_country_name
        AND UPPER(TRIM(r2.instance))            = UPPER(TRIM(s.city))
       LEFT OUTER JOIN
       ref_country_county_state_town_mapping    r3
         ON r3.country_code                     = s.nrm_country_code
        AND UPPER(TRIM(r3.town_city_name))      = UPPER(TRIM(s.county))       
       LEFT OUTER JOIN
       ref_country_county_state_town_mapping    r4
         ON r4.country_code                     = s.nrm_country_code
        AND UPPER(TRIM(r4.town_city_name))      = UPPER(TRIM(s.city))       
       LEFT OUTER JOIN 
       ref_workday_country_state_region         rx
         ON rx.country                          = s.nrm_country_name
        AND UPPER(TRIM(rx.instance))            = CASE
                                                   WHEN r0.county             IS NOT NULL THEN UPPER(TRIM(r0.county))
                                                   WHEN r1.instance           IS NOT NULL THEN UPPER(TRIM(r1.instance))
                                                   WHEN r2.instance           IS NOT NULL THEN UPPER(TRIM(r2.instance)) 
                                                   WHEN r3.county_state_name  IS NOT NULL THEN UPPER(TRIM(r3.county_state_name))
                                                   WHEN r4.county_state_name  IS NOT NULL THEN UPPER(TRIM(r4.county_state_name))
                                                   ELSE NULLIF(UPPER(TRIM(s.county)), '')
                                                  END
 WHERE NULLIF(TRIM(s.address_1), '') IS NOT NULL
   AND NULLIF(TRIM(s.address_1), '') NOT IN ('[Not Known]')
;
