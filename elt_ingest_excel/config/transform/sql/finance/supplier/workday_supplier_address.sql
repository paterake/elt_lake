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
     , s.nrm_county                                                           region
     , NULL                                                                   subregion
     , TRIM(s.city)                                                           city
     , NULL                                                                   submunicipality
     , TRIM(s.address_1)                                                      address_line_1
     , NULLIF(TRIM(s.address_2), '')                                          address_line_2
     , NULLIF(TRIM(s.address_3), '')                                          address_line_3
     , NULLIF(TRIM(s.addressline_4), '')                                      address_line_4
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
  FROM src_fin_supplier s
 WHERE s.address_1 IS NOT NULL
   AND TRIM(s.address_1) != ''
;
