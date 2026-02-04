DROP TABLE IF EXISTS workday_supplier_tax
;
CREATE TABLE workday_supplier_tax 
    AS
SELECT
       s.supplier_id                                                    supplier_id
     , s.nrm_vendor_name                                                supplier_name
     , COALESCE(TRIM(UPPER(s.country_code)), 'GB')                      tax_id_country
     , TRIM(REPLACE(REPLACE(s.tax_id_number, ' ', ''), '-', ''))        tax_id
     , CASE COALESCE(TRIM(UPPER(s.country_code)), 'GB')
         WHEN 'GB' THEN 'VAT_UK'
         WHEN 'US' THEN 'EIN'
         WHEN 'IE' THEN 'VAT_IE'
         WHEN 'FR' THEN 'VAT'
         WHEN 'DE' THEN 'VAT'
         WHEN 'ES' THEN 'VAT'
         WHEN 'IT' THEN 'VAT'
         WHEN 'NL' THEN 'VAT'
         WHEN 'BE' THEN 'VAT'
         WHEN 'PT' THEN 'VAT'
         WHEN 'AT' THEN 'VAT'
         WHEN 'SE' THEN 'VAT'
         WHEN 'DK' THEN 'VAT'
         WHEN 'FI' THEN 'VAT'
         ELSE 'Other'
       END                                                              tax_id_type
     , NULL                                                             primary_tax_id
     , NULL                                                             transaction_tax_id
     , COALESCE(TRIM(UPPER(s.country_code)), 'GB')                      tax_status_country
     , CASE
         WHEN s.tax_id_number IS NOT NULL AND TRIM(s.tax_id_number) != ''
         THEN 'Registered'
         ELSE 'Not_Registered'
       END                                                              tax_status
     , NULL                                                             transaction_tax_status
     , NULL                                                             withholding_tax_status
     , CASE
         WHEN COALESCE(TRIM(UPPER(s.country_code)), 'GB') = 'US'
              AND s.tax_id_number IS NOT NULL
         THEN '1099-MISC'
         ELSE NULL
       END                                                              tax_authority_form_type
     , CASE
         WHEN COALESCE(TRIM(UPPER(s.country_code)), 'GB') = 'US'
              AND s.tax_id_number IS NOT NULL
         THEN 'Yes'
         ELSE 'No'
       END                                                              irs_1099_supplier
     , NULL                                                             tax_document_date
     , NULL                                                             default_tax_code
     , NULL                                                             default_withholding_tax_code
     , 'FALSE'                                                          fatca
     , TRIM(s.tax_registration_number)                                  business_entity_tax_id
  FROM src_fin_supplier s
;
