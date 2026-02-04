DROP TABLE IF EXISTS workday_customer_related_worktags
;
CREATE TABLE workday_customer_related_worktags
    AS
SELECT
       c.customer_id                                 customer_id
     , c.customer_id_name                            customer_name
     , 'Sales_Territory'                             worktag_type
     , NULL                                          required_on_transaction
     , NULL                                          required_on_transaction_for_validation
     , NULL                                          delete_default_value
     , 'Sales_Territory_ID'                          worktag_id_type
     , TRIM(c.sales_territory)                       default_worktag_id_value
     , NULL                                          external_supplier_invoice_source
     , NULL                                          replace_all_allowed_values
     , NULL                                          delete_allowed_values
     , TRIM(c.sales_territory)                       allowed_worktag_id_value
  FROM src_fin_customer                c
 WHERE c.sales_territory IS NOT NULL
   AND TRIM(c.sales_territory) != ''
;
