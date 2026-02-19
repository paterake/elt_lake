DROP TABLE IF EXISTS workday_supplier_payment
;
CREATE TABLE workday_supplier_payment 
    AS
SELECT
       s.supplier_id                                     supplier_id
     , s.nrm_vendor_name                                 supplier_name
     , m.workday_payment_terms                           payment_terms
     , CASE
         WHEN s.nrm_currency_code = 'GBP'
         THEN 'BACS|EFT|Manual'
         WHEN s.nrm_currency_code = 'EUR'
         THEN 'SEPA|Wire|Manual'
         WHEN s.nrm_currency_code = 'USD'
         THEN 'Wire|EFT|Manual'
         WHEN s.nrm_currency_code IN ('CHF','AUD','PLN','SEK','AED','QAR','DKK','NOK')
         THEN 'Wire|Manual'
         ELSE 'BACS|EFT|Manual'
       END                                              payment_types_accepted
     , CASE
         WHEN s.nrm_currency_code = 'GBP'
         THEN 'EFT'
         WHEN s.nrm_currency_code = 'EUR'
         THEN 'SEPA'
         WHEN s.nrm_currency_code IN ('USD','CHF','AUD','SEK','AED','QAR','DKK','NOK')
         THEN 'Wire'
         ELSE 'BACS'
       END                                               default_payment_type
     , NULL                                              shipping_terms
     , NULL                                              always_separate_payments
     , NULL                                              do_not_pay_during_bank_account_updates
     , NULL                                              exclude_freight_amount_from_supplier_invoice_discount
     , NULL                                              exclude_other_charge_from_supplier_invoice_discount
     , NULL                                              exclude_tax_amount_from_supplier_invoice_discount
  FROM src_fin_supplier                                  s
       LEFT OUTER JOIN
       ref_source_supplier_payment_terms                 m
         ON  m.source_payment_terms                      = UPPER(TRIM(s.payment_terms_id))
;
