DROP TABLE IF EXISTS workday_supplier_procurement
;
CREATE TABLE workday_supplier_procurement 
    AS
SELECT
       TRIM(supplier_id)                                             supplier_id
     , TRIM(vendor_name)                                           supplier_name
     , CASE
         WHEN email_to_address IS NOT NULL AND TRIM(email_to_address) != ''
         THEN 'Email'
         ELSE 'Paper'
       END                                                         purchase_order_issue_option
     , FALSE                                                       invoice_any_supplier
     , TRIM(shipping_method)                                       shipping_method
     , FALSE                                                       acknowledgement_expected
     , FALSE                                                       enable_asn
     , NULL::INTEGER                                               asn_due_in_days
     , CAST(COALESCE(NULLIF(TRIM(minimum_order), ''), '0') AS DECIMAL(18,2))
                                                                   supplier_minimum_order_amount
     , COALESCE(TRIM(currency_id), TRIM(currencyid), 'GBP')        minimum_order_amount_currency
     , TRIM(comment1)                                              text_for_default_supplier_payment_memo
     , FALSE                                                       use_supplier_reference_as_default_supplier_payment_memo
     , TRUE                                                        use_invoice_memo_as_default_supplier_payment_memo
     , FALSE                                                       use_supplier_connection_memo
     , FALSE                                                       enable_global_location_number
     , FALSE                                                       disable_change_order
     , NULL                                                        multi_supplier_supplier_link_for_po_issue
     , NULL                                                        procurement_credit_card
     , FALSE                                                       edit_portal_taxes
     , CASE
         WHEN email_to_address IS NOT NULL AND TRIM(email_to_address) != ''
         THEN 'Email'
         ELSE 'Paper'
       END                                                         change_order_issue_option
  FROM src_fin_supplier
;
