DROP TABLE IF EXISTS workday_customer_currencies
;
CREATE TABLE workday_customer_currencies
    AS
SELECT
       c.customer_id                                  customer_id
     , c.customer_id_name                             customer_name
     , 'GBP'                                          accepted_currencies
     , 'GBP'                                          default_currency
  FROM src_fin_customer                c
;
