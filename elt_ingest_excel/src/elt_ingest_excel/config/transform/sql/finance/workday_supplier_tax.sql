DROP TABLE IF EXISTS workday_supplier_tax
;
CREATE TABLE workday_supplier_tax AS
SELECT
       TRIM(vendor_id)                                                supplier_id
     , TRIM(vendor_name)                                              supplier_name
     , COALESCE(TRIM(UPPER(country_code)), 'GB')                      tax_id_country
     , TRIM(REPLACE(REPLACE(tax_id_number, ' ', ''), '-', ''))        tax_id
     , CASE COALESCE(TRIM(UPPER(country_code)), 'GB')
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
       END                                                            tax_id_type
     , TRUE                                                           primary_tax_id
     , FALSE                                                          transaction_tax_id
     , COALESCE(TRIM(UPPER(country_code)), 'GB')                      tax_status_country
     , CASE
         WHEN tax_id_number IS NOT NULL AND TRIM(tax_id_number) != ''
         THEN 'Registered'
         ELSE 'Not_Registered'
       END                                                            tax_status
     , NULL                                                           transaction_tax_status
     , NULL                                                           withholding_tax_status
     , CASE
         WHEN COALESCE(TRIM(UPPER(country_code)), 'GB') = 'US'
              AND tax_id_number IS NOT NULL
         THEN '1099-MISC'
         ELSE NULL
       END                                                            tax_authority_form_type
     , CASE
         WHEN COALESCE(TRIM(UPPER(country_code)), 'GB') = 'US'
              AND tax_id_number IS NOT NULL
         THEN TRUE
         ELSE FALSE
       END                                                            irs_1099_supplier
     , NULL::DATE                                                     tax_document_date
     , NULL                                                           default_tax_code
     , NULL                                                           default_withholding_tax_code
     , FALSE                                                          fatca
     , TRIM(tax_registration_number)                                  business_entity_tax_id
  FROM src_fin_supplier
;
