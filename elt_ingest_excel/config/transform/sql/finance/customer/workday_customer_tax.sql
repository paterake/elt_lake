DROP TABLE IF EXISTS workday_customer_tax
;
CREATE TABLE workday_customer_tax
    AS
SELECT
       c.customer_id                                                            customer_id
     , c.nrm_customer_name                                                      customer_name
     , 'GBR 20% VAT (20%)'                                                      tax_code
     , fn_nvl2(c.nrm_tax_registration_number, NULL, c.nrm_country_name)         tax_id_country
     , c.nrm_tax_registration_number                                            tax_id
     , fn_nvl2(c.nrm_tax_registration_number, NULL, c.nrm_tax_id_type)         tax_id_type
     , fn_nvl2(c.nrm_tax_registration_number, NULL, 'Yes')                     primary_tax_id
     , fn_nvl2(c.nrm_tax_registration_number, NULL, 'Yes')                     transaction_tax_id
     , c.nrm_country_name                                                       tax_status_country
     , CASE
         WHEN UPPER(c.nrm_country_code) = 'GBR'
         THEN CASE
                WHEN c.nrm_tax_schedule_id = 'SOS'
                THEN 'Customer_or_Services'
                ELSE 'Customer_of_Goods'
              END
         WHEN UPPER(c.nrm_country_code) IN (
                'AT','BE','BG','HR','CY','CZ','DE','DK','EE','ES','FI','FR'
              , 'GR','HU','IE','IT','LT','LU','LV','MT','NL','PL','PT','RO'
              , 'SE','SI','SK'
              )
         THEN CASE
                WHEN c.nrm_tax_registration_number IS NOT NULL
                THEN 'EU_Company_VAT_Registered'
                WHEN c.nrm_tax_schedule_id = 'SZ'
                THEN 'EU_Company_Exempt'
                ELSE 'EU_Company_NOT_VAT_Registered_in_this_country'
              END
         ELSE CASE
                WHEN c.nrm_tax_registration_number IS NOT NULL
                THEN 'NON_EU_Company_VAT_Registered'
                ELSE 'Non_EU_Company_Not_VAT_registered_in_this_country'
              END
       END                                                                      transaction_tax_status
     , NULL                                                                     withholding_tax_status
  FROM src_fin_customer                                                         c
 WHERE c.nrm_tax_schedule_id                                                   = 'SS20'
;
