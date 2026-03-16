DROP TABLE IF EXISTS workday_customer_tax
;
CREATE TABLE workday_customer_tax
    AS
SELECT
       c.customer_id                                                             customer_id
     , c.nrm_customer_name                                                       customer_name
     , 'GBR 20% VAT (20%)'                                                       tax_code
     , fn_nvl2(c.nrm_tax_registration_number, NULL, c.nrm_country_name)          tax_id_country
     , c.nrm_tax_registration_number                                             tax_id
     , fn_nvl2(c.nrm_tax_registration_number, NULL, c.nrm_tax_id_type)           tax_id_type
     , fn_nvl2(c.nrm_tax_registration_number, NULL, 'Yes')                       primary_tax_id
     , fn_nvl2(c.nrm_tax_registration_number, NULL, 'Yes')                       transaction_tax_id
     , c.nrm_country_name                                                        tax_status_country
     , CASE
         WHEN UPPER(c.nrm_country_code) = 'GB'
         THEN CASE
                WHEN c.nrm_tax_schedule_id = 'SOS'
                THEN 'Customer of Services'
                ELSE 'Customer of Goods'
              END
         WHEN UPPER(c.nrm_country_code) IN (
                'AT','BE','BG','HR','CY','CZ','DE','DK','EE','ES','FI','FR'
              , 'GR','HU','IE','IT','LT','LU','LV','MT','NL','PL','PT','RO'
              , 'SE','SI','SK'
              )
         THEN CASE
                WHEN c.nrm_tax_registration_number IS NOT NULL
                THEN 'VAT Registered in THIS EU country- Domestic Scenario'
                WHEN c.nrm_tax_schedule_id = 'SZ'
                THEN 'EU Company - Exempt in THIS country'
                ELSE 'EU Company - Not Registered in this country'
              END
         ELSE CASE
                WHEN c.nrm_tax_registration_number IS NOT NULL
                THEN 'VAT Registered in THIS NON EU country- Domestic Scenario'
                ELSE 'Non EU Company Not VAT registered in this country'
              END
       END                                                                      transaction_tax_status
     , NULL                                                                     withholding_tax_status
  FROM src_fin_customer                                                         c
;
