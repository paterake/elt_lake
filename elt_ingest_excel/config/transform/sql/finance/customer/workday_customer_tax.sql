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
     , NULL                                           transaction_tax_status
     , NULL                                           withholding_tax_status
  FROM src_fin_customer                c
;
