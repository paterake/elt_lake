DROP TABLE IF EXISTS src_fin_customer
;
CREATE TABLE src_fin_customer
    AS
  WITH cte_customer
    AS (
SELECT t.*
  FROM src_fin_customer_dedup                            t
 WHERE rnk_score = 1
       )
     , cte_customer_rnk
    AS (
SELECT t.*
     , ROW_NUMBER() OVER(ORDER BY t.nrm_customer_name)   rnk
  FROM cte_customer                                      t
 WHERE t.nrm_payment_terms_id IS NOT NULL
       )
SELECT
       'C-' || LPAD(rnk::VARCHAR, 6, '0')                customer_id
     , t.*
  FROM cte_customer_rnk                                  t
;
