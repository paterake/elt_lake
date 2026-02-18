DROP TABLE IF EXISTS workday_customer_payment
;
CREATE TABLE workday_customer_payment
    AS
SELECT
       c.customer_id                                                    customer_id
     , c.nrm_customer_name                                              customer_name
     , COALESCE(NULLIF(UPPER(TRIM(c.payment_terms_id)), ''), '30 Days') payment_terms
     , CASE
         WHEN NULLIF(UPPER(TRIM(c.checkbook_id)), '') IS NULL
         THEN 'EFT'
         ELSE 'Manual'
       END                                                              default_payment_type
     , NULL                                                             interest_rule
     , NULL                                                             late_fee_rule
  FROM src_fin_customer                c
;
