DROP TABLE IF EXISTS workday_supplier_payment
;
CREATE TABLE workday_supplier_payment 
    AS
SELECT
       t.supplier_id                                     supplier_id
     , t.nrm_supplier_name                               supplier_name
     , t.nrm_payment_terms_id                            payment_terms
     , CASE
         WHEN t.nrm_currency_code         = 'GBP'
          AND t.nrm_bank_name             IS NOT NULL
          AND t.nrm_bank_sort_code        IS NOT NULL
          AND t.nrm_bank_account_number   IS NOT NULL
         THEN 'BACS|Manual'
         WHEN t.nrm_currency_code         = 'GBP'
          AND t.nrm_bank_iban             IS NOT NULL
         THEN 'Wire|Manual'
         WHEN t.nrm_currency_code         = 'EUR'
          AND t.nrm_bank_iban             IS NOT NULL
         THEN 'SEPA|Wire|Manual'
         WHEN t.nrm_currency_code         = 'EUR'
          AND t.nrm_bank_name             IS NOT NULL
          AND t.nrm_bank_sort_code        IS NOT NULL
          AND t.nrm_bank_account_number   IS NOT NULL
         THEN 'Wire|Manual'
         WHEN t.nrm_currency_code         = 'USD'
          AND t.nrm_bank_iban             IS NOT NULL
         THEN 'Wire|Manual'
         WHEN t.nrm_currency_code         = 'USD'
          AND t.nrm_bank_account_number   IS NOT NULL
          AND t.nrm_bank_swift_code       IS NOT NULL
         THEN 'Wire|Manual'
         WHEN t.nrm_currency_code         = 'USD'
          AND t.nrm_bank_name             IS NOT NULL
          AND t.nrm_bank_sort_code        IS NOT NULL
          AND t.nrm_bank_account_number   IS NOT NULL
         THEN 'Wire|Manual'
         WHEN t.nrm_currency_code         IN ('CHF','AUD','PLN','SEK','AED','QAR','DKK','NOK')
         THEN 'Wire|Manual'
         WHEN t.nrm_currency_code         IN ('CHF','AUD','PLN','SEK','AED','QAR','DKK','NOK')
          AND t.nrm_bank_name             IS NOT NULL
          AND t.nrm_bank_sort_code        IS NOT NULL
          AND t.nrm_bank_account_number   IS NOT NULL
         THEN 'Wire|Manual'
         ELSE 'Manual'
       END                                              payment_types_accepted
     , CASE
         WHEN t.nrm_currency_code         = 'GBP'
          AND t.nrm_bank_name             IS NOT NULL
          AND t.nrm_bank_sort_code        IS NOT NULL
          AND t.nrm_bank_account_number   IS NOT NULL
         THEN 'BACS'
         WHEN t.nrm_currency_code         = 'GBP'
          AND t.nrm_bank_iban             IS NOT NULL
         THEN 'Wire'
         WHEN t.nrm_currency_code         = 'EUR'
          AND t.nrm_bank_iban             IS NOT NULL
         THEN 'SEPA'
         WHEN t.nrm_currency_code         = 'EUR'
          AND t.nrm_bank_name             IS NOT NULL
          AND t.nrm_bank_sort_code        IS NOT NULL
          AND t.nrm_bank_account_number   IS NOT NULL
         THEN 'Wire'
         WHEN t.nrm_currency_code         = 'USD'
          AND t.nrm_bank_iban             IS NOT NULL
         THEN 'Wire'
         WHEN t.nrm_currency_code         = 'USD'
          AND t.nrm_bank_account_number   IS NOT NULL
          AND t.nrm_bank_swift_code       IS NOT NULL
         THEN 'Wire'
         WHEN t.nrm_currency_code         = 'USD'
          AND t.nrm_bank_name             IS NOT NULL
          AND t.nrm_bank_sort_code        IS NOT NULL
          AND t.nrm_bank_account_number   IS NOT NULL
         THEN 'Wire'
         WHEN t.nrm_currency_code         IN ('CHF','AUD','PLN','SEK','AED','QAR','DKK','NOK')
         THEN 'Wire'
         WHEN t.nrm_currency_code         IN ('CHF','AUD','PLN','SEK','AED','QAR','DKK','NOK')
          AND t.nrm_bank_name             IS NOT NULL
          AND t.nrm_bank_sort_code        IS NOT NULL
          AND t.nrm_bank_account_number   IS NOT NULL
         THEN 'Wire'
         ELSE 'Manual'
       END                                              default_payment_type
     , NULL                                              shipping_terms
     , NULL                                              always_separate_payments
     , NULL                                              do_not_pay_during_bank_account_updates
     , NULL                                              exclude_freight_amount_from_supplier_invoice_discount
     , NULL                                              exclude_other_charge_from_supplier_invoice_discount
     , NULL                                              exclude_tax_amount_from_supplier_invoice_discount
  FROM src_fin_supplier                t
 WHERE t.nrm_payment_terms_id          IS NOT NULL
;
