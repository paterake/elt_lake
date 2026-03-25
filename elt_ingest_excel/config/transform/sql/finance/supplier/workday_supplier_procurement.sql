DROP TABLE IF EXISTS workday_supplier_procurement
;
-- TEMPORARY: Business have said they won't populate this for now
-- When ready, remove WHERE FALSE and uncomment the real SELECT logic
CREATE TABLE workday_supplier_procurement
    AS
SELECT
       t.supplier_id                                     supplier_id
     , t.nrm_supplier_name                               supplier_name
     , CASE
         WHEN NULLIF(TRIM(t.nrm_agg_email_to_address), '') IS NOT NULL
         THEN 'Email'
         ELSE 'Paper'
       END                                               purchase_order_issue_option
     , CAST(NULL AS VARCHAR)                             invoice_any_supplier
     , CAST(NULL AS VARCHAR)                             shipping_method
     , CAST(NULL AS VARCHAR)                             acknowledgement_expected
     , CAST(NULL AS VARCHAR)                             enable_asn
     , CAST(NULL AS VARCHAR)                             asn_due_in_days
     , CAST(NULL AS VARCHAR)                             supplier_minimum_order_amount
     , CAST(NULL AS VARCHAR)                             minimum_order_amount_currency
     , CAST(NULL AS VARCHAR)                             text_for_default_supplier_payment_memo
     , CAST(NULL AS VARCHAR)                             use_supplier_reference_as_default_supplier_payment_memo
     , CAST(NULL AS VARCHAR)                             use_invoice_memo_as_default_supplier_payment_memo
     , CAST(NULL AS VARCHAR)                             use_supplier_connection_memo
     , CAST(NULL AS VARCHAR)                             enable_global_location_number
     , CAST(NULL AS VARCHAR)                             disable_change_order
     , CAST(NULL AS VARCHAR)                             multi_supplier_supplier_link_for_po_issue
     , CAST(NULL AS VARCHAR)                             procurement_credit_card
     , CAST(NULL AS VARCHAR)                             edit_portal_taxes
     , CAST(NULL AS VARCHAR)                             change_order_issue_option
  FROM src_fin_supplier                t
 GROUP BY
       supplier_id
;
