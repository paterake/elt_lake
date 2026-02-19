DROP TABLE IF EXISTS src_fin_supplier_raw
;
CREATE TABLE src_fin_supplier_raw
    AS
  WITH cte_supplier_src
    AS (
-- FA business unit
SELECT 'FA'   business_unit, t.* FROM fin_supplier_creditor_created_date_fa            t
UNION ALL
SELECT 'FA'   business_unit, t.* FROM fin_supplier_creditor_last_payment_date_fa       t
UNION ALL
SELECT 'FA'   business_unit, t.* FROM fin_supplier_creditor_last_purchase_date_fa      t
UNION ALL
-- NFC business unit
SELECT 'NFC'  business_unit, t.* FROM fin_supplier_creditor_created_date_nfc           t
UNION ALL
SELECT 'NFC'  business_unit, t.* FROM fin_supplier_creditor_last_payment_date_nfc      t
UNION ALL
SELECT 'NFC'  business_unit, t.* FROM fin_supplier_creditor_last_purchase_date_nfc     t
UNION ALL
-- WNSL business unit
SELECT 'WNSL' business_unit, t.* FROM fin_supplier_creditor_created_date_wnsl          t
UNION ALL
SELECT 'WNSL' business_unit, t.* FROM fin_supplier_creditor_last_payment_date_wnsl     t
UNION ALL
SELECT 'WNSL' business_unit, t.* FROM fin_supplier_creditor_last_purchase_date_wnsl    t
       )
     , cte_supplier_nrm
    AS (
SELECT 
       TRIM(t.vendor_id)                                          vendor_id
     , TRIM(t.vendor_name)                                        nrm_vendor_name
     , UPPER(TRIM(t.vendor_name))                                 key_vendor_name
     , COALESCE(
          TRY_STRPTIME(NULLIF(TRIM(t.created_date        ), ''), '%Y-%m-%d %H:%M:%S')
        , TRY_STRPTIME(NULLIF(TRIM(t.created_date        ), ''), '%Y-%m-%d')
        , TRY_STRPTIME(NULLIF(TRIM(t.created_date        ), ''), '%d-%m-%Y')
       )                                                          created_ts
     , COALESCE(
          TRY_STRPTIME(NULLIF(TRIM(t.last_payment_date   ), ''), '%Y-%m-%d %H:%M:%S')
        , TRY_STRPTIME(NULLIF(TRIM(t.last_payment_date   ), ''), '%Y-%m-%d')
        , TRY_STRPTIME(NULLIF(TRIM(t.last_payment_date   ), ''), '%d-%m-%Y')
       )                                                          last_payment_ts
     , COALESCE(
          TRY_STRPTIME(NULLIF(TRIM(t.last_purchase_date  ), ''), '%Y-%m-%d %H:%M:%S')
        , TRY_STRPTIME(NULLIF(TRIM(t.last_purchase_date  ), ''), '%Y-%m-%d')
        , TRY_STRPTIME(NULLIF(TRIM(t.last_purchase_date  ), ''), '%d-%m-%Y')
       )                                                          last_purchase_ts
     , t.*
  FROM cte_supplier_src                      t
 WHERE NULLIF(TRIM(t.payment_terms_id), '')  IS NULL
       ) 
     , cte_supplier_distinct
    AS (
SELECT DISTINCT 
       t.*
     , mbu.target_value                      target_business_unit
  FROM cte_supplier_nrm                      t
       INNER JOIN
       ref_source_business_unit_mapping      mbu
          ON UPPER(mbu.source_value)         = UPPER(TRIM(t.business_unit))
       )
     , cte_supplier_business_unit
    AS (
SELECT t.key_vendor_name
     , ARRAY_AGG (DISTINCT t.business_unit              ORDER BY t.business_unit       ) array_business_unit
     , ARRAY_AGG (DISTINCT t.target_business_unit       ORDER BY t.target_business_unit) array_target_business_unit
     , STRING_AGG(DISTINCT t.business_unit        , '|' ORDER BY t.business_unit       ) pipe_business_unit
     , STRING_AGG(DISTINCT t.target_business_unit , '|' ORDER BY t.target_business_unit) pipe_target_business_unit
  FROM cte_supplier_distinct           t
 GROUP BY 
       t.key_vendor_name
       )
     , cte_supplier
    AS (
SELECT 
       COUNT() OVER (PARTITION BY t.vendor_id)                             vendor_id_count
     , RANK() OVER (PARTITION BY t.vendor_id ORDER BY t.nrm_vendor_name)   vendor_id_rnk
     , ROW_NUMBER() OVER
       (
         PARTITION BY t.key_vendor_name
           ORDER BY
              CASE
                 WHEN NULLIF(UPPER(TRIM(t.bank_name)), '') IS NOT NULL
                  AND NULLIF(UPPER(TRIM(t.bank_name)), '') <> 'BANK NAME'
                 THEN 0
                 ELSE 1
              END ASC NULLS LAST
            , CASE
                 WHEN NULLIF(UPPER(TRIM(t.eft_bank_account)), '') IS NOT NULL
                 THEN 0
                 ELSE 1
              END ASC NULLS LAST
            , t.created_ts DESC  NULLS LAST
       )                                                                   data_rnk
     , COUNT() OVER(PARTITION BY t.key_vendor_name)                        key_count
     , t.* 
     , bu.array_business_unit
     , bu.pipe_business_unit
     , bu.pipe_target_business_unit
  FROM cte_supplier_distinct      t
       INNER JOIN
       cte_supplier_business_unit bu
         ON bu.key_vendor_name    = t.key_vendor_name
       )
SELECT 
       CASE 
         WHEN t.vendor_id_count > 1 
         THEN t.vendor_id || '_' || t.vendor_id_rnk::VARCHAR
         ELSE t.vendor_id
       END                                                                 nrm_vendor_id
     , t.*
  FROM cte_supplier              t
 WHERE t.data_rnk = 1
