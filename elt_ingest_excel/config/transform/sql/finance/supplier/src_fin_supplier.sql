DROP TABLE IF EXISTS src_fin_supplier
;
CREATE TABLE src_fin_supplier
    AS
  WITH cte_supplier
    AS (
SELECT t.*
  FROM src_fin_supplier_rnk                              t
 WHERE rnk_score = 1
       )
     , cte_supplier_rnk
    AS (
SELECT t.*
     , ROW_NUMBER() OVER(ORDER BY t.nrm_supplier_name)   rnk
  FROM cte_supplier                                      t
 WHERE t.nrm_payment_terms_id IS NOT NULL
       )
SELECT
       'S-' || LPAD(rnk::VARCHAR, 6, '0')                supplier_id
     , t.*
  FROM cte_supplier_rnk                                  t
;
