DROP TABLE IF EXISTS workday_supplier_address
;
CREATE TABLE workday_supplier_address 
    AS
  WITH cte_address
    AS (
SELECT
       t.supplier_id                                                          supplier_id
     , t.nrm_supplier_name                                                    supplier_name
     , CAST(NULL AS VARCHAR)                                                  formatted_address
     , CAST(NULL AS VARCHAR)                                                  address_format_type
     , CAST(NULL AS VARCHAR)                                                  defaulted_business_site_address
     , CAST(NULL AS VARCHAR)                                                  delete_flag
     , CAST(NULL AS VARCHAR)                                                  do_not_replace_all
     , strftime(CAST(t.nrm_created_date AS DATE), '%d/%m/%Y')                 last_modified
     , CAST(NULL AS VARCHAR)                                                  descriptor
     , ROW_NUMBER() OVER (
           PARTITION BY t.supplier_id
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
     , CAST(NULL AS VARCHAR)                                                  subregion
     , u.address.nrm_city                                                     city
     , CAST(NULL AS VARCHAR)                                                  submunicipality
     , u.address.nrm_address_line_1                                           address_line_1
     , u.address.nrm_address_line_2                                           address_line_2
     , u.address.nrm_address_line_3                                           address_line_3
     , u.address.nrm_address_line_4                                           address_line_4
     , u.address.nrm_postal_code                                              postal_code
     , 'Yes'                                                                  public_flag
     , 'Yes'                                                                  primary_flag
     , CAST(NULL AS VARCHAR)                                                  effective_date
     , CAST(NULL AS VARCHAR)                                                  address_type
     , CAST(NULL AS VARCHAR)                                                  use_for
     , CAST(NULL AS VARCHAR)                                                  use_for_tenanted
     , CAST(NULL AS VARCHAR)                                                  address_comments
     , CAST(NULL AS VARCHAR)                                                  number_of_days
     , CAST(NULL AS VARCHAR)                                                  municipality_local
  FROM src_fin_supplier                         t
     , UNNEST(nrm_array_address) u(address)
 WHERE COALESCE( NULLIF(TRIM(u.address.nrm_address_line_1), '')
               , NULLIF(TRIM(u.address.nrm_address_line_2), '')
               , NULLIF(TRIM(u.address.nrm_address_line_3), '')
               , NULLIF(TRIM(u.address.nrm_address_line_4), '')
               ) IS NOT NULL
   AND NULLIF(TRIM(u.address.nrm_address_line_1), '') NOT IN ('[Not Known]') 
   AND NULLIF(TRIM(u.address.nrm_postal_code)   , '') IS NOT NULL
   AND NULLIF(TRIM(u.address.nrm_region)        , '') IS NOT NULL
       )
SELECT t.supplier_id
     , t.supplier_name
     , t.formatted_address
     , t.address_format_type
     , t.defaulted_business_site_address
     , t.delete_flag
     , t.do_not_replace_all
     , t.last_modified
     , t.descriptor
     , TRIM(t.supplier_id) || '_' || t.address_id_code || '_' || t.address_id_rnk   address_id
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
     , t.public_flag
     , CASE t.address_id_rnk WHEN 1 THEN 'Yes' ELSE 'No' END                        is_primary
     , t.effective_date
     , t.address_type
     , t.use_for
     , t.use_for_tenanted
     , t.address_comments
     , t.number_of_days
     , t.municipality_local
  FROM cte_address                     t
 ORDER BY 
       t.supplier_id
;
