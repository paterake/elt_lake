DROP TABLE IF EXISTS src_fin_supplier
;
CREATE TABLE src_fin_supplier
    AS
  WITH cte_supplier_src
    AS (
-- FA business unit
SELECT 'FA'   AS business_unit, *   FROM fin_supplier_creditor_created_date_fa
UNION ALL
SELECT 'FA'   AS business_unit, *   FROM fin_supplier_creditor_last_payment_date_fa
UNION ALL
SELECT 'FA'   AS business_unit, *   FROM fin_supplier_creditor_last_purchase_date_fa
UNION ALL
-- NFC business unit
SELECT 'NFC'  AS business_unit, *   FROM fin_supplier_creditor_created_date_nfc
UNION ALL
SELECT 'NFC'  AS business_unit, *   FROM fin_supplier_creditor_last_payment_date_nfc
UNION ALL
SELECT 'NFC'  AS business_unit, *   FROM fin_supplier_creditor_last_purchase_date_nfc
UNION ALL
-- WNSL business unit
SELECT 'WNSL' AS business_unit, *   FROM fin_supplier_creditor_created_date_wnsl
UNION ALL
SELECT 'WNSL' AS business_unit, *   FROM fin_supplier_creditor_last_payment_date_wnsl
UNION ALL
SELECT 'WNSL' AS business_unit, *   FROM fin_supplier_creditor_last_purchase_date_wnsl
       )
     , cte_supplier_distinct
    AS (
SELECT DISTINCT
       *
  FROM cte_supplier_src
       )
     , cte_supplier_rnk
    AS (
SELECT t.*
     , ROW_NUMBER() OVER
       (PARTITION BY business_unit, vendor_id
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
     , ROW_NUMBER() OVER (ORDER BY business_unit, vendor_name)  rnk
  FROM cte_supplier_rnk
 WHERE data_rnk = 1
       )
SELECT
        'S-' || LPAD(rnk::VARCHAR, 6, '0')   supplier_id
      , TRIM(t.vendor_name)                  nrm_vendor_name
      , r.country_code                       nrm_country_code
      , r.language_code                      nrm_language_code
      , r.currency_code                      nrm_currency_code
      , r.phone_code                         nrm_phone_code
      , r.tax_id_type                        nrm_tax_id_type
      , r.country_name                       nrm_country_name
      , t.*
  FROM cte_supplier                          t
       -- First try: match on country name (higher population)
       LEFT OUTER JOIN
       ref_supplier_country_mapping          m_name
          ON  m_name.source_country_name     = TRIM(t.country)
          AND m_name.source_country_code     IS NULL
       -- Second try: match on country code (fallback)
       LEFT OUTER JOIN
       ref_supplier_country_mapping          m_code
          ON  m_code.source_country_code     = NULLIF(UPPER(TRIM(t.country_code)), '')
          AND m_code.source_country_name     IS NULL
       -- Join to reference table using: name match > code match > default GB
       LEFT OUTER JOIN
       ref_supplier_country                  r
          ON r.country_code                  = COALESCE(m_name.country_code, m_code.country_code, 'GB')
;
