DROP TABLE IF EXISTS workday_customer_related_worktags
;
CREATE TABLE workday_customer_related_worktags
    AS
SELECT
       c.customer_id                                  customer_id
     , c.nrm_customer_name                            customer_name
     , 'Customer'                                     worktag_type
     , NULL                                           required_on_transaction
     , NULL                                           required_on_transaction_for_validation
     , NULL                                           delete_default_value
     , NULL                                           worktag_id_type
     , NULL                                           default_worktag_id_value
     , NULL                                           external_supplier_invoice_source
     , NULL                                           replace_all_allowed_values
     , NULL                                           delete_allowed_values
     , NULL                                           allowed_worktag_id_value
  FROM src_fin_customer                c
;
