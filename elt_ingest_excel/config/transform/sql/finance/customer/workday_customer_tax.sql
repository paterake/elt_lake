DROP TABLE IF EXISTS workday_customer_tax
;
CREATE TABLE workday_customer_tax
    AS
SELECT
       c.customer_id                                  customer_id
     , c.nrm_customer_name                            customer_name
     , TRIM(c.tax_schedule_id)                        tax_code
     , c.nrm_country_name                             tax_id_country
     , TRIM(REPLACE(REPLACE(c.tax_registration_number, ' ', ''), '-', ''))
                                                      tax_id
     , c.nrm_tax_id_type                              tax_id_type
     , NULL                                           primary_tax_id
     , NULL                                           transaction_tax_id
     , c.nrm_country_name                             tax_status_country
     , CASE
         WHEN NULLIF(TRIM(c.tax_schedule_id), '') IS NULL
          AND NULLIF(TRIM(c.tax_registration_number), '') IS NULL
         THEN NULL
         WHEN UPPER(TRIM(c.nrm_country_code)) IN (
                'AT','BE','BG','HR','CY','CZ','DE','DK','EE','ES','FI','FR'
              , 'GR','HU','IE','IT','LT','LU','LV','MT','NL','PL','PT','RO'
              , 'SE','SI','SK'
              )
         THEN CASE
                WHEN NULLIF(TRIM(c.tax_registration_number), '') IS NOT NULL
                 AND UPPER(TRIM(c.tax_schedule_id)) IN ('SS20')
                THEN 'VAT Registered in THIS EU country- Domestic Scenario'
                WHEN NULLIF(TRIM(c.tax_registration_number), '') IS NOT NULL
                 AND UPPER(TRIM(c.tax_schedule_id)) IN ('SZ')
                THEN 'EU Company - Exempt in THIS country'
                WHEN NULLIF(TRIM(c.tax_registration_number), '') IS NULL
                THEN 'EU Company - Not Registered in this country'
                ELSE 'EU Company - Not Registered in this country'
              END
         ELSE CASE
                WHEN UPPER(TRIM(c.nrm_country_code)) = 'GB'
                 AND (
                        NULLIF(TRIM(c.tax_registration_number), '') IS NOT NULL
                     OR UPPER(TRIM(c.nrm_tax_id_type)) LIKE 'VAT%'
                     )
                 AND UPPER(TRIM(c.tax_schedule_id)) IN ('SS20')
                THEN 'VAT Registered in THIS NON EU country- Domestic Scenario'
                WHEN NULLIF(TRIM(c.tax_registration_number), '') IS NOT NULL
                THEN 'Non-MAR Company - Non-Resident Taxpayer Registered for VAT'
                WHEN UPPER(TRIM(c.tax_schedule_id)) IN ('SOS')
                THEN 'Import or Export (Outside of EU when company is EU)'
                ELSE 'Non EU Company Not VAT registered in this country'
              END
       END                                            transaction_tax_status
     , NULL                                           withholding_tax_status
  FROM src_fin_customer                      c
 WHERE NULLIF(TRIM(c.tax_schedule_id), '')   = 'SS20'
;
