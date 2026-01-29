DROP TABLE IF EXISTS workday_customer_currencies
;
CREATE TABLE workday_customer_currencies
    AS
SELECT
       TRIM(customer_id)                             customer_id
     , TRIM(customer_name)                           customer_name
     , 'GBP'                                         accepted_currencies
     , 'GBP'                                         default_currency
  FROM src_fin_customer
;
