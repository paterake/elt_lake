DROP TABLE IF EXISTS workday_customer_settlement_account
;
CREATE TABLE workday_customer_settlement_account
    AS
SELECT
       c.customer_id                                                       customer_id
     , c.nrm_customer_name                                                 customer_name
     , TRIM(c.customer_id) || '_BANK'                                      settlement_bank_account_id
     , c.nrm_country_name                                                  country
     , c.nrm_currency_code                                                 currency
     , COALESCE(NULLIF(TRIM(c.statement_name), ''), c.nrm_customer_name)   bank_account_nickname
     , 'Checking'                                                          bank_account_type
     , NULL                                                                bank_name
     , NULL                                                                routing_transit_number
     , NULL                                                                branch_id
     , NULL                                                                branch_name
     , NULL                                                                bank_account_number
     , NULL                                                                check_digit
     , COALESCE(NULLIF(TRIM(c.statement_name), ''), c.nrm_customer_name)   name_on_account
     , NULL                                                                roll_number
     , NULL                                                                iban
     , NULL                                                                swift_bank_identification_code
     , CASE
         WHEN c.nrm_currency_code = 'GBP'
         THEN 'BACS'
         WHEN c.nrm_currency_code = 'EUR'
         THEN 'SEPA'
         WHEN c.nrm_currency_code IN ('USD','CHF','AUD','SEK','AED','QAR','DKK','NOK')
         THEN 'Wire'
         ELSE 'BACS'
       END                                                                 accepts_payment_types
     , CASE
         WHEN c.nrm_currency_code = 'GBP'
         THEN 'BACS'
         WHEN c.nrm_currency_code = 'EUR'
         THEN 'SEPA'
         WHEN c.nrm_currency_code IN ('USD','CHF','AUD','SEK','AED','QAR','DKK','NOK')
         THEN 'Wire'
         ELSE 'BACS'
       END                                                                 payment_types
     , NULL                                                                for_supplier_connections_only
     , NULL                                                                requires_prenote
     , NULL                                                                payment_type_prenote
     , CASE
         WHEN UPPER(TRIM(c.inactive)) = 'NO'         
         THEN 'No'
         ELSE 'Yes'
       END                                            inactive
     , NULL                                           bank_instructions
  FROM src_fin_customer                c
 WHERE c.checkbook_id IS NOT NULL
   AND TRIM(c.checkbook_id) != ''
   AND 1 = 2
;
