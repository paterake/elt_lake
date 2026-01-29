DROP TABLE IF EXISTS workday_customer_tax
;
CREATE TABLE workday_customer_tax
    AS
SELECT
       TRIM(customer_id)                             customer_id
     , TRIM(customer_name)                           customer_name
     , TRIM(tax_schedule_id)                         tax_code
     , COALESCE(TRIM(UPPER(country_code)), 'GB')     tax_id_country
     , TRIM(REPLACE(REPLACE(tax_registration_number, ' ', ''), '-', ''))
                                                     tax_id
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
       END                                           tax_id_type
     , NULL                                          primary_tax_id
     , NULL                                          transaction_tax_id
     , COALESCE(TRIM(UPPER(country_code)), 'GB')     tax_status_country
     , CASE
         WHEN tax_registration_number IS NOT NULL
          AND TRIM(tax_registration_number) != ''
         THEN 'Registered'
         ELSE 'Not_Registered'
       END                                           transaction_tax_status
     , NULL                                          withholding_tax_status
  FROM src_fin_customer
;
