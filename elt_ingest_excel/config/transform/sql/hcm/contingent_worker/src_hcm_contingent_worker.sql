DROP TABLE IF EXISTS src_hcm_contingent_worker
;
CREATE TABLE src_hcm_contingent_worker
    AS
  WITH cte_contingent_worker_base
    AS (
SELECT * FROM hcm_contingent_worker
       )
     , cte_contingent_worker_distinct
    AS (
SELECT DISTINCT *
  FROM cte_contingent_worker_base
       )
     , cte_contingent_worker_rnk
    AS (
SELECT t.*
     , ROW_NUMBER() OVER
       (PARTITION BY username
            ORDER BY
              created_date          DESC NULLS LAST
       ) data_rnk
  FROM cte_contingent_worker_distinct t
       )
     , cte_contingent_worker
    AS (
SELECT *
     , ROW_NUMBER() OVER (ORDER BY username, user_id) + 100000  rnk
  FROM cte_contingent_worker_rnk
 WHERE data_rnk = 1
       )
SELECT
        'CW-' || LPAD(rnk::VARCHAR, 6, '0') AS contingent_worker_id
      , t.*
  FROM cte_contingent_worker t
;
