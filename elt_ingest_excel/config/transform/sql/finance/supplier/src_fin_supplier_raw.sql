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
SELECT DISTINCT
       TRIM(t.vendor_id)                        nrm_vendor_id
     , TRIM(t.vendor_name)                      nrm_vendor_name
     , COALESCE(
          TRY_STRPTIME(NULLIF(TRIM(t.created_date        ), ''), '%Y-%m-%d %H:%M:%S')
        , TRY_STRPTIME(NULLIF(TRIM(t.created_date        ), ''), '%Y-%m-%d')
        , TRY_STRPTIME(NULLIF(TRIM(t.created_date        ), ''), '%d-%m-%Y')
       )                                        created_ts
     , COALESCE(
          TRY_STRPTIME(NULLIF(TRIM(t.last_payment_date   ), ''), '%Y-%m-%d %H:%M:%S')
        , TRY_STRPTIME(NULLIF(TRIM(t.last_payment_date   ), ''), '%Y-%m-%d')
        , TRY_STRPTIME(NULLIF(TRIM(t.last_payment_date   ), ''), '%d-%m-%Y')
       )                                        last_payment_ts
     , COALESCE(
          TRY_STRPTIME(NULLIF(TRIM(t.last_purchase_date  ), ''), '%Y-%m-%d %H:%M:%S')
        , TRY_STRPTIME(NULLIF(TRIM(t.last_purchase_date  ), ''), '%Y-%m-%d')
        , TRY_STRPTIME(NULLIF(TRIM(t.last_purchase_date  ), ''), '%d-%m-%Y')
       )                                        last_purchase_ts
     , t.* 
  FROM cte_supplier_src t
;