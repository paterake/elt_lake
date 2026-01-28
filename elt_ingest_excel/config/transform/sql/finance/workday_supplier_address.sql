DROP TABLE IF EXISTS workday_supplier_address
;
CREATE TABLE workday_supplier_address 
    AS
SELECT
       TRIM(supplier_id)                                                   supplier_id
     , TRIM(vendor_name)                                                   supplier_name
     , NULL                                                                formatted_address
     , NULL                                                                address_format_type
     , NULL                                                                defaulted_business_site_address
     , NULL                                                                delete_flag
     , NULL                                                                do_not_replace_all
     , created_date                                                        last_modified
     , COALESCE(TRIM(vendor_address_code_primary), 'MAIN')                 descriptor
     , TRIM(supplier_id) || '_' || COALESCE(TRIM(vendor_address_code_primary), 'MAIN')
                                                                           address_id
     , TRIM(country)                                                       country
     , TRIM(UPPER(country_code))                                           country_code
     , TRIM(county)                                                        region
     , NULL                                                                subregion
     , TRIM(city)                                                          city
     , NULL                                                                submunicipality
     , TRIM(address_1)                                                     address_line_1
     , NULLIF(TRIM(address_2), '')                                         address_line_2
     , NULLIF(TRIM(address_3), '')                                         address_line_3
     , NULLIF(TRIM(addressline_4), '')                                     address_line_4
     , TRIM(UPPER(post_code))                                              postal_code
     , TRUE                                                                public_flag
     , TRUE                                                                primary_flag
     , created_date                                                        effective_date
     , 'Business'                                                          address_type
     , CASE COALESCE(UPPER(TRIM(vendor_address_code_primary)), 'MAIN')
         WHEN 'MAIN'      THEN 'Business'
         WHEN 'PRIMARY'   THEN 'Business'
         WHEN 'REMIT'     THEN 'Payment'
         WHEN 'PURCHASE'  THEN 'Purchase_Order'
         WHEN 'SHIP FROM' THEN 'Shipping'
         ELSE 'Business'
       END                                                                 use_for
     , NULL                                                                use_for_tenanted
     , TRIM(COALESCE(comment1, comment2))                                  address_comments
     , NULL::INTEGER                                                       number_of_days
     , NULL                                                                municipality_local
  FROM src_fin_supplier
 WHERE address_1 IS NOT NULL
   AND TRIM(address_1) != ''
;
