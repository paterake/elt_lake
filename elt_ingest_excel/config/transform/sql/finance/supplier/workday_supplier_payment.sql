DROP TABLE IF EXISTS workday_supplier_payment
;
CREATE TABLE workday_supplier_payment 
    AS
SELECT
       TRIM(supplier_id)                           supplier_id
     , TRIM(vendor_name)                           supplier_name
     , TRIM(payment_terms_id)                      payment_terms
     , CASE
         WHEN eft_transfer_method IS NOT NULL AND TRIM(eft_transfer_method) != ''
         THEN CASE UPPER(TRIM(eft_transfer_method))
                WHEN 'ACH'        THEN 'ACH'
                WHEN 'WIRE'       THEN 'Wire'
                WHEN 'ELECTRONIC' THEN 'ACH'
                ELSE 'ACH'
              END
         WHEN checkbook_id IS NOT NULL
         THEN 'Check'
         ELSE 'Check'
       END                                         payment_types_accepted
     , CASE
         WHEN eft_transfer_method IS NOT NULL AND TRIM(eft_transfer_method) != ''
         THEN CASE UPPER(TRIM(eft_transfer_method))
                WHEN 'ACH'        THEN 'ACH'
                WHEN 'WIRE'       THEN 'Wire'
                WHEN 'ELECTRONIC' THEN 'ACH'
                ELSE 'ACH'
              END
         WHEN checkbook_id IS NOT NULL
         THEN 'Check'
         ELSE 'Check'
       END                                         default_payment_type
     , TRIM(shipping_method)                       shipping_terms
     , NULL                                        always_separate_payments
     , NULL                                        do_not_pay_during_bank_account_updates
     , NULL                                        exclude_freight_amount_from_supplier_invoice_discount
     , NULL                                        exclude_other_charge_from_supplier_invoice_discount
     , NULL                                        exclude_tax_amount_from_supplier_invoice_discount
  FROM src_fin_supplier
;
