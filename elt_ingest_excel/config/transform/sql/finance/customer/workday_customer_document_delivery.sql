DROP TABLE IF EXISTS workday_customer_document_delivery
;
CREATE TABLE workday_customer_document_delivery
    AS
SELECT
       c.customer_id                                  customer_id
     , c.nrm_customer_name                            customer_name
     , NULL                                           always_separate_payments
     , NULL                                           remit_from_customer
     , CASE
         WHEN c.email_to_address IS NOT NULL
          AND TRIM(c.email_to_address) != ''
         THEN 'Email'
         ELSE 'Print'
       END                                            invoice_delivery_method
     , TRIM(LOWER(c.email_to_address))                invoice_notification_email_recipients
     , CASE
         WHEN c.email_to_address IS NOT NULL
          AND TRIM(c.email_to_address) != ''
         THEN 'Email'
         ELSE 'Print'
       END                                            statement_delivery_method
     , TRIM(LOWER(c.email_to_address))                statement_notification_email_recipients
     , CASE
         WHEN NULLIF(UPPER(TRIM(c.email_to_address)), '') IS NULL
         THEN 'Print'
         ELSE 'Email'
       END                                            dunning_delivery_method
     , TRIM(LOWER(c.email_to_address))                dunning_letter_notification_email_recipients
     , NULL                                           electronic_invoicing_start_date
     , NULL                                           electronic_invoicing_government_issued_customer_id
     , NULL                                           electronic_invoicing_intermediary_vendor_id
     , NULL                                           electronic_invoicing_vendor_issued_customer_id
     , NULL                                           mandate_required
     , NULL                                           direct_debit_payment_type
     , NULL                                           default_mandate
  FROM src_fin_customer                c
 WHERE NULLIF(UPPER(TRIM(c.email_to_address)), '') IS NOT NULL
;
