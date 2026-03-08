DROP TABLE IF EXISTS workday_supplier_payment
;
CREATE TABLE workday_supplier_payment 
    AS
SELECT
       t.supplier_id                                     supplier_id
     , t.nrm_supplier_name                               supplier_name
     , t.nrm_payment_terms_id                            payment_terms
     , CASE
         WHEN t.nrm_currency_code = 'GBP'
         THEN 'BACS|EFT|Manual'
         WHEN t.nrm_currency_code = 'EUR'
         THEN 'SEPA|Wire|Manual'
         WHEN t.nrm_currency_code = 'USD'
         THEN 'Wire|EFT|Manual'
         WHEN t.nrm_currency_code IN ('CHF','AUD','PLN','SEK','AED','QAR','DKK','NOK')
         THEN 'Wire|Manual'
         ELSE 'BACS|EFT|Manual'
       END                                              payment_types_accepted
     , CASE
         WHEN t.nrm_currency_code = 'GBP'
         THEN 'EFT'
         WHEN t.nrm_currency_code = 'EUR'
         THEN 'SEPA'
         WHEN t.nrm_currency_code IN ('USD','CHF','AUD','SEK','AED','QAR','DKK','NOK')
         THEN 'Wire'
         ELSE 'BACS'
       END                                               default_payment_type
     , NULL                                              shipping_terms
     , NULL                                              always_separate_payments
     , NULL                                              do_not_pay_during_bank_account_updates
     , NULL                                              exclude_freight_amount_from_supplier_invoice_discount
     , NULL                                              exclude_other_charge_from_supplier_invoice_discount
     , NULL                                              exclude_tax_amount_from_supplier_invoice_discount
  FROM src_fin_supplier                t
 WHERE t.nrm_payment_terms_id          IS NOT NULL
   AND COALESCE(NULLIF(TRIM(t.eft_bank_account), ''), NULLIF(TRIM(t.iban), '')) IS NOT NULL
;
