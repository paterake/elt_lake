DROP TABLE IF EXISTS src_fin_customer
;
CREATE TABLE src_fin_customer
    AS
  WITH cte_customer_src
    AS (
SELECT * FROM fin_customer_debtor_last_3_years
UNION
SELECT * FROM fin_customer_debtor_created_date
UNION
SELECT * FROM fin_customer_debtor_last_payment_date
       )
     , cte_customer_distinct
    AS (
SELECT DISTINCT *
  FROM cte_customer_src
       )
     , cte_customer_rnk
    AS (
SELECT t.*
     , ROW_NUMBER() OVER
       (PARTITION BY customer_number
            ORDER BY
              last_payment_date     DESC NULLS LAST
            , last_transaction_date DESC NULLS LAST
            , created_date          DESC NULLS LAST
       ) data_rnk
  FROM cte_customer_distinct                     t
       )
     , cte_customer
    AS (
SELECT *
     , ROW_NUMBER() OVER (ORDER BY customer_name, customer_number)  rnk
  FROM cte_customer_rnk
 WHERE data_rnk = 1
       )
SELECT
        'C-' || LPAD(rnk::VARCHAR, 6, '0') AS customer_id
      , t.*
  FROM cte_customer t
;
