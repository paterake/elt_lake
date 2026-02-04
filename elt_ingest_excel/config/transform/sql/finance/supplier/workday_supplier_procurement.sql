DROP TABLE IF EXISTS workday_supplier_procurement
;
-- TEMPORARY: Business have said they won't populate this for now
-- When ready, remove WHERE FALSE and uncomment the real SELECT logic
CREATE TABLE workday_supplier_procurement
    AS
SELECT
       TRIM(s.supplier_id)                                             supplier_id
     , TRIM(s.vendor_name)                                             supplier_name
     , CASE
         WHEN s.email_to_address IS NOT NULL AND TRIM(s.email_to_address) != ''
         THEN 'Email'
         ELSE 'Paper'
       END                                                           purchase_order_issue_option
     , NULL                                                          invoice_any_supplier
     , TRIM(s.shipping_method)                                         shipping_method
     , NULL                                                          acknowledgement_expected
     , NULL                                                          enable_asn
     , NULL                                                          asn_due_in_days
     , COALESCE(NULLIF(TRIM(s.minimum_order), ''), '0')                supplier_minimum_order_amount
     , COALESCE(TRIM(s.currency_id), TRIM(s.currencyid), 'GBP')          minimum_order_amount_currency
     , TRIM(s.comment1)                                                text_for_default_supplier_payment_memo
     , NULL                                                          use_supplier_reference_as_default_supplier_payment_memo
     , NULL                                                          use_invoice_memo_as_default_supplier_payment_memo
     , NULL                                                          use_supplier_connection_memo
     , NULL                                                          enable_global_location_number
     , NULL                                                          disable_change_order
     , NULL                                                          multi_supplier_supplier_link_for_po_issue
     , NULL                                                          procurement_credit_card
     , NULL                                                          edit_portal_taxes
     , NULL                                                          change_order_issue_option
  FROM src_fin_supplier s
 WHERE FALSE
;
