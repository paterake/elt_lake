DROP TABLE IF EXISTS src_fin_supplier
;
CREATE TABLE src_fin_supplier 
    AS
  WITH cte_supplier_src
    AS (
SELECT * FROM rpatel.main.fin_supplier_creditor_created_date
UNION
SELECT * FROM rpatel.main.fin_supplier_creditor_last_payment_date
UNION
SELECT * FROM rpatel.main.fin_supplier_creditor_last_purchase_date
       )
     , cte_supplier_distinct
    AS (
SELECT DISTINCT *
  FROM cte_supplier_src
       )
     , cte_supplier_rnk
    AS (
SELECT t.*
     , ROW_NUMBER() OVER 
       (PARTITION BY vendor_id
            ORDER BY
              last_payment_date  DESC NULLS LAST
            , last_purchase_date DESC NULLS LAST
            , created_date       DESC NULLS LAST
       ) data_rnk
  FROM cte_supplier_distinct                     t
       )
     , cte_supplier
    AS (
SELECT *
     , ROW_NUMBER() OVER (ORDER BY vendor_name)  rnk
  FROM cte_supplier_rnk
 WHERE data_rnk = 1
       )
SELECT 
        'S-' || LPAD(rnk::VARCHAR, 6, '0') AS supplier_id
      , t.*
  FROM cte_supplier t
;
