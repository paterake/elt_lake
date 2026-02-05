DROP TABLE IF EXISTS workday_supplier_tax
;
CREATE TABLE workday_supplier_tax 
    AS
SELECT
       s.supplier_id                                                    supplier_id
     , s.nrm_vendor_name                                                supplier_name
     , s.nrm_country_code                                               tax_id_country
     , TRIM(REPLACE(REPLACE(s.tax_id_number, ' ', ''), '-', ''))        tax_id
     , COALESCE(s.nrm_tax_id_type, 'Other')                             tax_id_type
     , NULL                                                             primary_tax_id
     , NULL                                                             transaction_tax_id
     , s.nrm_country_code                                               tax_status_country
     , CASE
         WHEN s.tax_id_number IS NOT NULL AND TRIM(s.tax_id_number) != ''
         THEN 'Registered'
         ELSE 'Not_Registered'
       END                                                              tax_status
     , NULL                                                             transaction_tax_status
     , NULL                                                             withholding_tax_status
     , CASE
         WHEN s.nrm_country_code = 'US'
              AND s.tax_id_number IS NOT NULL
         THEN '1099-MISC'
         ELSE NULL
       END                                                              tax_authority_form_type
     , CASE
         WHEN s.nrm_country_code = 'US'
              AND s.tax_id_number IS NOT NULL
         THEN 'Yes'
         ELSE 'No'
       END                                                              irs_1099_supplier
     , NULL                                                             tax_document_date
     , NULL                                                             default_tax_code
     , NULL                                                             default_withholding_tax_code
     , 'FALSE'                                                          fatca
     , TRIM(s.tax_registration_number)                                  business_entity_tax_id
  FROM src_fin_supplier                s
;
