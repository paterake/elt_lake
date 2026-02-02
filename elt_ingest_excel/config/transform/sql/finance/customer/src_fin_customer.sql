DROP TABLE IF EXISTS src_fin_customer
;
CREATE TABLE src_fin_customer
    AS
  WITH cte_customer_src
    AS (
-- FA business unit
SELECT 'FA'   AS business_unit, *   FROM fin_customer_debtor_last_3_years_fa
UNION ALL
SELECT 'FA'   AS business_unit, *   FROM fin_customer_debtor_created_date_fa
UNION ALL
SELECT 'FA'   AS business_unit, *   FROM fin_customer_debtor_last_payment_date_fa
UNION ALL
-- NFC business unit
SELECT 'NFC'  AS business_unit, *   FROM fin_customer_debtor_last_3_years_nfc
UNION ALL
SELECT 'NFC'  AS business_unit, *   FROM fin_customer_debtor_created_date_nfc
UNION ALL
SELECT 'NFC'  AS business_unit, *   FROM fin_customer_debtor_last_payment_date_nfc
UNION ALL
-- WNSL business unit
SELECT 'WNSL' AS business_unit, *   FROM fin_customer_debtor_last_3_years_wnsl
UNION ALL
SELECT 'WNSL' AS business_unit, *   FROM fin_customer_debtor_created_date_wnsl
UNION ALL
SELECT 'WNSL' AS business_unit, *   FROM fin_customer_debtor_last_payment_date_wnsl
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
       (PARTITION BY business_unit, customer_number
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
     , ROW_NUMBER() OVER (ORDER BY business_unit, customer_name, customer_number)  rnk
  FROM cte_customer_rnk
 WHERE data_rnk = 1
       )
SELECT
        'C-' || LPAD(rnk::VARCHAR, 6, '0') AS customer_id
      , t.*
  FROM cte_customer t
;
