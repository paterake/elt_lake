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
     , cte_customer_base
    AS (
SELECT DISTINCT
       TRIM(t.customer_number)                                                                        nrm_customer_number
     , UPPER(COALESCE(NULLIF(UPPER(TRIM(t.customer_name)), ''), NULLIF(TRIM(t.customer_number), ''))) nrm_customer_name
     , t.*
  FROM cte_customer_src                      t
       )
     , cte_customer_nrm
    AS (
SELECT DISTINCT
       UPPER(REGEXP_REPLACE(REGEXP_REPLACE(REPLACE(t.nrm_customer_name, '.', ''), '[^a-zA-Z0-9\s]', '', 'g'), '(\s|\b)(LTD|LIMITED|PLC|GROUP|HOLDINGS|FC|FOOTBALL|CLUB|ASSOCIATION)\b', '', 'gi')) 
       clean_name
     , COALESCE(
          TRY_STRPTIME(NULLIF(TRIM(t.created_date          ), ''), '%Y-%m-%d %H:%M:%S')
        , TRY_STRPTIME(NULLIF(TRIM(t.created_date          ), ''), '%Y-%m-%d')
        , TRY_STRPTIME(NULLIF(TRIM(t.created_date          ), ''), '%d-%m-%Y')
       )                                                                                              nrm_created_date
     , COALESCE(
          TRY_STRPTIME(NULLIF(TRIM(t.last_payment_date     ), ''), '%Y-%m-%d %H:%M:%S')
        , TRY_STRPTIME(NULLIF(TRIM(t.last_payment_date     ), ''), '%Y-%m-%d')
        , TRY_STRPTIME(NULLIF(TRIM(t.last_payment_date     ), ''), '%d-%m-%Y')
       )                                                                                              nrm_last_payment_date
     , COALESCE(
          TRY_STRPTIME(NULLIF(TRIM(t.last_transaction_date ), ''), '%Y-%m-%d %H:%M:%S')
        , TRY_STRPTIME(NULLIF(TRIM(t.last_transaction_date ), ''), '%Y-%m-%d')
        , TRY_STRPTIME(NULLIF(TRIM(t.last_transaction_date ), ''), '%d-%m-%Y')
       )                                                                                              nrm_last_transaction_date
     , mbu.target_value                                                                               nrm_business_unit
     , t.*
  FROM cte_customer_base                     t
       INNER JOIN
       ref_source_business_unit_mapping      mbu
          ON UPPER(mbu.source_value)         = UPPER(TRIM(t.business_unit))
       ) 
     , cte_customer_name_agg
    AS (
SELECT t.nrm_customer_name
     , ARRAY_AGG (DISTINCT t.nrm_business_unit      ORDER BY t.nrm_business_unit) array_nrm_business_unit
     , STRING_AGG(DISTINCT t.nrm_business_unit, '|' ORDER BY t.nrm_business_unit) pipe_nrm_business_unit
  FROM cte_customer_nrm                      t
 GROUP BY 
       t.nrm_customer_name
       )
     , cte_customer_rank
    AS (
SELECT 
       COUNT() OVER (PARTITION BY t.nrm_customer_number)                               nrm_customer_id_count
     , COUNT() OVER(PARTITION BY t.nrm_customer_name)                                  nrm_customer_name_count
     , RANK() OVER (PARTITION BY t.nrm_customer_number ORDER BY t.nrm_customer_name)   nrm_customer_id_rnk
     , ROW_NUMBER() OVER
       (
         PARTITION BY t.nrm_customer_name
             ORDER BY
                   t.nrm_created_date           ASC  NULLS LAST
                 , t.nrm_last_payment_date      DESC NULLS LAST
                 , t.nrm_last_transaction_date  DESC NULLS LAST
       )                                                                         data_rnk
     , t.* 
     , agg.array_nrm_business_unit
     , agg.pipe_nrm_business_unit
  FROM cte_customer_nrm                t
       INNER JOIN
       cte_customer_name_agg           agg
         ON agg.nrm_customer_name      = t.nrm_customer_name
       )
SELECT 
       t.*
  FROM cte_customer_rank               t
;
