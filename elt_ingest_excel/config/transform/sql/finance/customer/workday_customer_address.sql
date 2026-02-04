DROP TABLE IF EXISTS workday_customer_address
;
CREATE TABLE workday_customer_address
    AS
SELECT
       c.customer_id                                  customer_id
     , c.customer_id_name                             customer_name
     , NULL                                           formatted_address
     , NULL                                           address_format_type
     , NULL                                           defaulted_business_site_address
     , NULL                                           delete_flag
     , NULL                                           do_not_replace_all
     , c.created_date                                 last_modified
     , NULL                                           descriptor
     , TRIM(c.customer_id) || '_' || COALESCE(TRIM(c.address_code), 'MAIN')
                                                      address_id
     , TRIM(c.country)                                country
     , c.nrm_country_code                             country_code
     , TRIM(c.county)                                 region
     , NULL                                           subregion
     , TRIM(c.city)                                   city
     , NULL                                           submunicipality
     , TRIM(c.address_1)                              address_line_1
     , NULLIF(TRIM(c.address_2), '')                  address_line_2
     , NULLIF(TRIM(c.address_3), '')                  address_line_3
     , NULL                                           address_line_4
     , TRIM(UPPER(c.post_code))                       postal_code
     , 'Yes'                                          is_public
     , 'Yes'                                          is_primary
     , TRIM(c.address_code)                           address_type
     , c.created_date                                 effective_date
     , TRIM(c.address_code)                           use_for
     , NULL                                           use_for_tenanted
     , TRIM(COALESCE(c.comment1, c.comment2))         customer_comment
     , NULL                                           number_of_days
     , NULL                                           municipality_local
     , NULL                                           optional_address
  FROM src_fin_customer                c
 WHERE c.address_1 IS NOT NULL
   AND TRIM(c.address_1) != ''
;
