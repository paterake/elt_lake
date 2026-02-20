DROP TABLE IF EXISTS src_fin_customer_raw
;
CREATE TABLE src_fin_customer_raw
    AS
  WITH cte_customer_src
    AS (
-- FA business unit
SELECT 'FA'   business_unit, t.* FROM fin_customer_debtor_last_3_years_fa      t
UNION ALL
SELECT 'FA'   business_unit, t.* FROM fin_customer_debtor_created_date_fa      t
UNION ALL
SELECT 'FA'   business_unit, t.* FROM fin_customer_debtor_last_payment_date_fa t
UNION ALL
-- NFC business unit
SELECT 'NFC'  business_unit, t.* FROM fin_customer_debtor_last_3_years_nfc     t
UNION ALL
SELECT 'NFC'  business_unit, t.* FROM fin_customer_debtor_created_date_nfc     t
UNION ALL
SELECT 'NFC'  business_unit, t.* FROM fin_customer_debtor_last_payment_date_nfc t
UNION ALL
-- WNSL business unit
SELECT 'WNSL' business_unit, t.* FROM fin_customer_debtor_last_3_years_wnsl    t
UNION ALL
SELECT 'WNSL' business_unit, t.* FROM fin_customer_debtor_created_date_wnsl    t
UNION ALL
SELECT 'WNSL' business_unit, t.* FROM fin_customer_debtor_last_payment_date_wnsl t
       )
     , cte_customer_time_nrm
    AS (
SELECT DISTINCT
       TRIM(t.customer_number)                                                                        customer_number
     , COALESCE(NULLIF(UPPER(TRIM(t.customer_name)), ''), NULLIF(TRIM(t.customer_number), ''))        nrm_customer_name
     , UPPER(COALESCE(NULLIF(UPPER(TRIM(t.customer_name)), ''), NULLIF(TRIM(t.customer_number), ''))) key_customer_name
     , COALESCE(
          TRY_STRPTIME(NULLIF(TRIM(t.created_date          ), ''), '%Y-%m-%d %H:%M:%S')
        , TRY_STRPTIME(NULLIF(TRIM(t.created_date          ), ''), '%Y-%m-%d')
        , TRY_STRPTIME(NULLIF(TRIM(t.created_date          ), ''), '%d-%m-%Y')
       )                                                                                              created_ts
     , COALESCE(
          TRY_STRPTIME(NULLIF(TRIM(t.last_payment_date     ), ''), '%Y-%m-%d %H:%M:%S')
        , TRY_STRPTIME(NULLIF(TRIM(t.last_payment_date     ), ''), '%Y-%m-%d')
        , TRY_STRPTIME(NULLIF(TRIM(t.last_payment_date     ), ''), '%d-%m-%Y')
       )                                                                                              last_payment_ts
     , COALESCE(
          TRY_STRPTIME(NULLIF(TRIM(t.last_transaction_date ), ''), '%Y-%m-%d %H:%M:%S')
        , TRY_STRPTIME(NULLIF(TRIM(t.last_transaction_date ), ''), '%Y-%m-%d')
        , TRY_STRPTIME(NULLIF(TRIM(t.last_transaction_date ), ''), '%d-%m-%Y')
       )                                                                                              last_transaction_ts
     , t.*
     , mbu.target_value                                                                               target_business_unit
  FROM cte_customer_src                      t
       INNER JOIN
       ref_source_business_unit_mapping      mbu
          ON UPPER(mbu.source_value)         = UPPER(TRIM(t.business_unit))
       ) 
     , cte_customer_business_unit
    AS (
SELECT t.key_customer_name
     , ARRAY_AGG (DISTINCT t.business_unit              ORDER BY t.business_unit       ) array_business_unit
     , ARRAY_AGG (DISTINCT t.target_business_unit       ORDER BY t.target_business_unit) array_target_business_unit
     , STRING_AGG(DISTINCT t.business_unit        , '|' ORDER BY t.business_unit       ) pipe_business_unit
     , STRING_AGG(DISTINCT t.target_business_unit , '|' ORDER BY t.target_business_unit) pipe_target_business_unit
  FROM cte_customer_time_nrm           t
 GROUP BY 
       t.key_customer_name
       )
     , cte_customer
    AS (
SELECT 
       COUNT() OVER (PARTITION BY t.customer_number)                             customer_id_count
     , RANK() OVER (PARTITION BY t.customer_number ORDER BY t.nrm_customer_name) customer_id_rnk
     , ROW_NUMBER() OVER
       (
         PARTITION BY t.key_customer_name
             ORDER BY
                   t.created_ts          ASC  NULLS LAST
                 , t.last_payment_ts     DESC NULLS LAST
                 , t.last_transaction_ts DESC NULLS LAST
       )                                                             data_rnk
     , COUNT() OVER(PARTITION BY t.key_customer_name)                key_count
     , t.* 
     , bu.array_business_unit
  FROM cte_customer_time_nrm           t
       INNER JOIN
       cte_customer_business_unit      bu
         ON bu.key_customer_name       = t.key_customer_name
       )
SELECT 
       CASE 
         WHEN t.customer_id_count > 1 
         THEN t.customer_number || '_' || t.customer_id_rnk::VARCHAR
         ELSE t.customer_number
       END                                                           nrm_customer_number
     , t.*
  FROM cte_customer                    t
;
