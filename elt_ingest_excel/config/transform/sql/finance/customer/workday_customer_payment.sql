DROP TABLE IF EXISTS workday_customer_payment
;
CREATE TABLE workday_customer_payment
    AS
SELECT
       c.customer_id                                     customer_id
     , c.nrm_customer_name                               customer_name
     , m.workday_payment_terms                           payment_terms
     , CASE
         WHEN c.nrm_currency_code = 'GBP'
         THEN 'EFT'
         WHEN c.nrm_currency_code = 'EUR'
         THEN 'SEPA'
         WHEN c.nrm_currency_code IN ('USD','CHF','AUD','SEK','AED','QAR','DKK','NOK')
         THEN 'Wire'
         ELSE 'BACS'
       END                                               default_payment_type
     , NULL                                              interest_rule
     , NULL                                              late_fee_rule
  FROM src_fin_customer                                  c
       LEFT OUTER JOIN
       ref_source_supplier_payment_terms                 m
         ON  m.source_payment_terms                      = UPPER(TRIM(c.payment_terms_id))

;
