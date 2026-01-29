DROP TABLE IF EXISTS workday_customer_address
;
CREATE TABLE workday_customer_address
    AS
SELECT
       TRIM(customer_id)                             customer_id
     , TRIM(customer_name)                           customer_name
     , NULL                                          formatted_address
     , NULL                                          address_format_type
     , NULL                                          defaulted_business_site_address
     , NULL                                          delete_flag
     , NULL                                          do_not_replace_all
     , created_date                                  last_modified
     , NULL                                          descriptor
     , TRIM(customer_id) || '_' || COALESCE(TRIM(address_code), 'MAIN')
                                                     address_id
     , TRIM(country)                                 country
     , TRIM(UPPER(country_code))                     country_code
     , TRIM(county)                                  region
     , NULL                                          subregion
     , TRIM(city)                                    city
     , NULL                                          submunicipality
     , TRIM(address_1)                               address_line_1
     , NULLIF(TRIM(address_2), '')                   address_line_2
     , NULLIF(TRIM(address_3), '')                   address_line_3
     , NULL                                          address_line_4
     , TRIM(UPPER(post_code))                        postal_code
     , 'Yes'                                         public
     , 'Yes'                                         primary
     , TRIM(address_code)                            type
     , created_date                                  effective_date
     , TRIM(address_code)                            use_for
     , NULL                                          use_for_tenanted
     , TRIM(COALESCE(comment1, comment2))            comments
     , NULL                                          number_of_days
     , NULL                                          municipality_local
     , NULL                                          address
  FROM src_fin_customer
 WHERE address_1 IS NOT NULL
   AND TRIM(address_1) != ''
;
