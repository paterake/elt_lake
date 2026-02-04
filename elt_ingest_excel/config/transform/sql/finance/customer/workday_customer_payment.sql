DROP TABLE IF EXISTS workday_customer_payment
;
CREATE TABLE workday_customer_payment
    AS
SELECT
       c.customer_id                                 customer_id
     , TRIM(c.customer_name)                         customer_name
     , TRIM(c.payment_terms_id)                      payment_terms
     , CASE
         WHEN c.checkbook_id IS NOT NULL
          AND TRIM(c.checkbook_id) != ''
         THEN 'Check'
         ELSE 'ACH'
       END                                           default_payment_type
     , NULL                                          interest_rule
     , NULL                                          late_fee_rule
  FROM src_fin_customer                c
;
