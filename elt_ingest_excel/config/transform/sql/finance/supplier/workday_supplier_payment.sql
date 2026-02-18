DROP TABLE IF EXISTS workday_supplier_payment
;
CREATE TABLE workday_supplier_payment 
    AS
SELECT
       s.supplier_id                                  supplier_id
     , s.nrm_vendor_name                              supplier_name
     , m.workday_payment_terms                        payment_terms
     , CASE
         WHEN s.eft_transfer_method IS NOT NULL AND TRIM(s.eft_transfer_method) != ''
         THEN CASE
                WHEN UPPER(TRIM(s.eft_transfer_method)) = 'ACH'
                THEN 'ACH'
                WHEN UPPER(TRIM(s.eft_transfer_method)) = 'WIRE'
                THEN 'Wire'
                WHEN UPPER(TRIM(s.eft_transfer_method)) = 'ELECTRONIC'
                THEN 'ACH'
                ELSE 'ACH'
              END
         WHEN s.checkbook_id IS NOT NULL
         THEN 'Check'
         ELSE 'Check'
       END                                              payment_types_accepted
     , CASE
         WHEN s.eft_transfer_method IS NOT NULL AND TRIM(s.eft_transfer_method) != ''
         THEN CASE
                WHEN UPPER(TRIM(s.eft_transfer_method)) = 'ACH'
                THEN 'ACH'
                WHEN UPPER(TRIM(s.eft_transfer_method)) = 'WIRE'
                THEN 'Wire'
                WHEN UPPER(TRIM(s.eft_transfer_method)) = 'ELECTRONIC'
                THEN 'ACH'
                ELSE 'ACH'
              END
         WHEN s.checkbook_id IS NOT NULL
         THEN 'Check'
         ELSE 'Check'
       END                                              default_payment_type
     , TRIM(s.shipping_method)                        shipping_terms
     , NULL                                           always_separate_payments
     , NULL                                           do_not_pay_during_bank_account_updates
     , NULL                                           exclude_freight_amount_from_supplier_invoice_discount
     , NULL                                           exclude_other_charge_from_supplier_invoice_discount
     , NULL                                           exclude_tax_amount_from_supplier_invoice_discount
  FROM src_fin_supplier                                s
       LEFT OUTER JOIN
       ref_source_supplier_payment_terms               m
         ON  UPPER(TRIM(s.payment_terms_id))         = m.source_payment_terms
;
