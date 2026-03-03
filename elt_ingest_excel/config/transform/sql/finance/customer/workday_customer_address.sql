DROP TABLE IF EXISTS workday_customer_address
;
CREATE TABLE workday_customer_address
    AS
SELECT
       c.customer_id                                                          customer_id
     , c.nrm_customer_name                                                    customer_name
     , NULL                                                                   formatted_address
     , NULL                                                                   address_format_type
     , NULL                                                                   defaulted_business_site_address
     , NULL                                                                   delete_flag
     , NULL                                                                   do_not_replace_all
     , NULL                                                                   last_modified
     , NULL                                                                   descriptor
     , TRIM(c.customer_id) || '_' || COALESCE(TRIM(c.address_code), 'MAIN')   address_id
     , c.nrm_country_name                                                     country
     , c.nrm_country_code                                                     country_code
     , c.nrm_region                                                           region
     , NULL                                                                   subregion
     , c.nrm_city                                                             city
     , NULL                                                                   submunicipality
     , c.nrm_address_line_1                                                   address_line_1
     , c.nrm_address_line_2                                                   address_line_2
     , c.nrm_address_line_3                                                   address_line_3
     , c.nrm_address_line_4                                                   address_line_4
     , c.nrm_postal_code                                                      postal_code
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
  FROM src_fin_customer                         c
 WHERE COALESCE(NULLIF(TRIM(c.nrm_address_line_1), ''), NULLIF(TRIM(c.nrm_address_line_2), ''), NULLIF(TRIM(c.nrm_address_line_3), '')) IS NOT NULL
   AND NULLIF(TRIM(c.nrm_address_line_1), '') NOT IN ('[Not Known]') 
;
