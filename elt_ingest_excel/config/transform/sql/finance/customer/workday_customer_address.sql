DROP TABLE IF EXISTS workday_customer_address
;
CREATE TABLE workday_customer_address
    AS
  WITH cte_address
    AS (
SELECT
       t.customer_id                                                          customer_id
     , t.nrm_customer_name                                                    customer_name
     , NULL                                                                   formatted_address
     , NULL                                                                   address_format_type
     , NULL                                                                   defaulted_business_site_address
     , NULL                                                                   delete_flag
     , NULL                                                                   do_not_replace_all
     , NULL                                                                   last_modified
     , NULL                                                                   descriptor
     , ROW_NUMBER() OVER (
           PARTITION BY t.customer_id
               ORDER BY u.address.nrm_address_code
                      , u.address.nrm_address_line_1
                      , u.address.nrm_address_line_2
                      , u.address.nrm_address_line_3
                      , u.address.nrm_address_line_4
                      , u.address.nrm_city
                      , u.address.nrm_region
                      , u.address.nrm_postal_code
                      , u.address.nrm_country_name
       )                                                                      address_id_rnk
     , u.address.nrm_address_code                                             address_id_code
     , u.address.nrm_country_name                                             country
     , u.address.nrm_country_code                                             country_code
     , u.address.nrm_region                                                   region
     , NULL                                                                   subregion
     , u.address.nrm_city                                                     city
     , NULL                                                                   submunicipality
     , u.address.nrm_address_line_1                                           address_line_1
     , u.address.nrm_address_line_2                                           address_line_2
     , u.address.nrm_address_line_3                                           address_line_3
     , u.address.nrm_address_line_4                                           address_line_4
     , u.address.nrm_postal_code                                              postal_code
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
  FROM src_fin_customer                         t
     , UNNEST(nrm_array_customer_address) u(address)
 WHERE COALESCE( NULLIF(TRIM(u.address.nrm_address_line_1), '')
               , NULLIF(TRIM(u.address.nrm_address_line_2), '')
               , NULLIF(TRIM(u.address.nrm_address_line_3), '')) IS NOT NULL
   AND NULLIF(TRIM(u.address.nrm_address_line_1), '') NOT IN ('[Not Known]') 
   AND NULLIF(TRIM(u.address.nrm_postal_code)   , '') IS NOT NULL
   AND NULLIF(TRIM(u.address.nrm_region)        , '') IS NOT NULL
       )
SELECT t.customer_id
     , t.customer_name
     , t.formatted_address
     , t.address_format_type
     , t.defaulted_business_site_address
     , t.delete_flag
     , t.do_not_replace_all
     , t.last_modified
     , t.descriptor
     , TRIM(t.customer_id) || '_' || t.address_id_code || '_' || t.address_id_rnk   address_id
     , t.country
     , t.country_code
     , t.region
     , t.subregion
     , t.city
     , t.submunicipality
     , t.address_line_1
     , t.address_line_2
     , t.address_line_3
     , t.address_line_4
     , t.postal_code
     , t.is_public
     , CASE t.address_id_rnk WHEN 1 THEN 'Yes' ELSE 'No' END                                 is_primary
     , t.address_type   
     , t.effective_date
     , t.use_for
     , t.use_for_tenanted
     , t.customer_comment
     , t.number_of_days
     , t.municipality_local
     , t.optional_address
  FROM cte_address                     t
;
