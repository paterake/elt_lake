DROP TABLE IF EXISTS workday_supplier_tax
;
CREATE TABLE workday_supplier_tax 
    AS
SELECT
       s.supplier_id                                                    supplier_id
     , s.nrm_vendor_name                                                supplier_name
     , s.nrm_country_name                                               tax_id_country
     , CASE
         WHEN s.nrm_country_code = 'GB'
         THEN CASE
                WHEN NULLIF(REPLACE(REPLACE(s.tax_registration_number, ' ', ''), '-', ''), '') ~ '^[0-9]{9}$'
                THEN TRIM(REPLACE(REPLACE(s.tax_registration_number, ' ', ''), '-', ''))
                WHEN NULLIF(REPLACE(REPLACE(s.tax_id_number, ' ', ''), '-', ''), '') ~ '^[A-Za-z0-9]{8}$'
                THEN TRIM(REPLACE(REPLACE(s.tax_id_number, ' ', ''), '-', ''))
                WHEN NULLIF(REPLACE(REPLACE(s.tax_id_number, ' ', ''), '-', ''), '') ~ '^[0-9]{10}$'
                THEN TRIM(REPLACE(REPLACE(s.tax_id_number, ' ', ''), '-', ''))
                ELSE COALESCE(
                       NULLIF(TRIM(s.tax_id_number), ''),
                       NULLIF(TRIM(s.tax_registration_number), '')
                     )
              END
         ELSE COALESCE(
                NULLIF(TRIM(s.tax_id_number), ''),
                NULLIF(TRIM(s.tax_registration_number), '')
              )
       END                                                              tax_id
     , CASE
         WHEN s.nrm_country_code = 'GB'
         THEN CASE
                WHEN NULLIF(REPLACE(REPLACE(s.tax_registration_number, ' ', ''), '-', ''), '') ~ '^[0-9]{9}$'
                THEN 'VAT Reg No'
                WHEN NULLIF(REPLACE(REPLACE(s.tax_id_number, ' ', ''), '-', ''), '') ~ '^[A-Za-z0-9]{8}$'
                THEN 'Company Number'
                WHEN NULLIF(REPLACE(REPLACE(s.tax_id_number, ' ', ''), '-', ''), '') ~ '^[0-9]{10}$'
                THEN 'UTR - Unique Taxpayer Reference'
                ELSE NULL
              END
         ELSE COALESCE(dm.tax_id_type_label, 'TIN')
       END                                                              tax_id_type
     , 'Yes'                                                            primary_tax_id
     , CASE
         WHEN s.nrm_country_code = 'GB'
              AND NULLIF(REPLACE(REPLACE(s.tax_registration_number, ' ', ''), '-', ''), '') ~ '^[0-9]{9}$'
         THEN 'Yes'
         WHEN s.nrm_country_code != 'GB'
              AND dm.tax_id_type_label ILIKE '%VAT%'
         THEN 'Yes'
         ELSE 'No'
       END                                                              transaction_tax_id
     , s.nrm_country_name                                               tax_status_country
     , CASE
         WHEN COALESCE(
                NULLIF(TRIM(s.tax_id_number), ''),
                NULLIF(TRIM(s.tax_registration_number), '')
              ) IS NOT NULL
         THEN 'Registered'
         ELSE 'Not_Registered'
       END                                                              tax_status
     , NULL                                                             transaction_tax_status
     , NULL                                                             withholding_tax_status
     , CASE
         WHEN s.nrm_country_code = 'US'
              AND s.tax_id_number IS NOT NULL
         THEN '1099 MISC'
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
     , 'No'                                                             fatca
     , CASE
         WHEN s.nrm_country_code = 'GB'
              AND NULLIF(REPLACE(REPLACE(s.tax_id_number, ' ', ''), '-', ''), '') ~ '^[A-Za-z0-9]{8}$'
         THEN NULLIF(TRIM(s.tax_registration_number), '')
         ELSE NULL
       END                                                              business_entity_tax_id
  FROM src_fin_supplier                s
       LEFT OUTER JOIN
       ref_country_tax_id_type_mapping dm
         ON  dm.country_code          = s.nrm_country_code
         AND dm.is_default            = TRUE
 WHERE COALESCE(
          NULLIF(TRIM(s.tax_id_number), ''),
          NULLIF(TRIM(s.tax_registration_number), '')
       ) IS NOT NULL
;
