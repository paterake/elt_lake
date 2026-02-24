DROP TABLE IF EXISTS workday_supplier_tax
;
CREATE TABLE workday_supplier_tax 
    AS
SELECT
       s.supplier_id                                                    supplier_id
     , s.nrm_vendor_name                                                supplier_name
     , s.nrm_country_name                                               tax_id_country
     , NULLIF(TRIM(s.tax_id_number), '')                                tax_id
     , CASE
         WHEN s.nrm_country_code = 'GB'
         THEN CASE
                WHEN NULLIF(TRIM(s.tax_id_number), '') IS NOT NULL
                THEN CASE
                        WHEN NULLIF(REPLACE(REPLACE(s.tax_registration_number, ' ', ''), '-', ''), '') ~ '^[0-9]{9}$'
                        THEN 'VAT Reg No'
                        WHEN NULLIF(REPLACE(REPLACE(s.tax_id_number, ' ', ''), '-', ''), '') ~ '^[A-Za-z0-9]{8}$'
                        THEN 'Company Number'
                        WHEN NULLIF(REPLACE(REPLACE(s.tax_id_number, ' ', ''), '-', ''), '') ~ '^[0-9]{10}$'
                        THEN 'UTR - Unique Taxpayer Reference'
                        ELSE 'VAT Reg No'
                     END
                ELSE NULL
              END
         ELSE COALESCE(dm.tax_id_type_label, 'TIN')
       END                                                              tax_id_type
     , 'Yes'                                                            primary_tax_id
     , NULL                                                             transaction_tax_id
     , s.nrm_country_name                                               tax_status_country
     , NULL                                                             tax_status
     , s.tax_schedule_id                                                transaction_tax_status
     , NULL                                                             withholding_tax_status
     , NULL                                                             tax_authority_form_type
     , NULL                                                             irs_1099_supplier
     , NULL                                                             tax_document_date
     , NULL                                                             default_tax_code
     , NULL                                                             default_withholding_tax_code
     , NULL                                                             fatca
     , NULL                                                             business_entity_tax_id
  FROM src_fin_supplier                s
       LEFT OUTER JOIN
       ref_country_tax_id_type_mapping dm
         ON  dm.country_code           = s.nrm_country_code
         AND dm.is_default             = TRUE
 WHERE 
       s.tax_schedule_id                  = 'PS20'
   AND NULLIF(TRIM(s.tax_id_number), '')  IS NOT NULL
;
