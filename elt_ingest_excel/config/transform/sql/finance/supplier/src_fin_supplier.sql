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
     , cte_supplier_per_bu
    AS (
SELECT *
  FROM cte_supplier_rnk
 WHERE data_rnk = 1
       )
     , cte_supplier_primary
    AS (
SELECT t.*
     , ROW_NUMBER() OVER
       (PARTITION BY vendor_id
            ORDER BY created_date DESC NULLS LAST
       ) primary_rnk
  FROM cte_supplier_per_bu                         t
       )
     , cte_supplier_business_units
    AS (
SELECT vendor_id
     , ARRAY_AGG(DISTINCT business_unit ORDER BY business_unit)  business_units
  FROM cte_supplier_per_bu
 GROUP BY vendor_id
       )
     , cte_supplier
    AS (
SELECT t.*
     , bu.business_units
     , ROW_NUMBER() OVER (ORDER BY t.vendor_id)  rnk
  FROM cte_supplier_primary                      t
       INNER JOIN
       cte_supplier_business_units               bu
          ON bu.vendor_id                        = t.vendor_id
 WHERE t.primary_rnk = 1
       )
SELECT
        'S-' || LPAD(rnk::VARCHAR, 6, '0')      supplier_id
      , TRIM(t.vendor_name)                     nrm_vendor_name
      , r.country_code                          nrm_country_code
      , r.language_code                         nrm_language_code
      , r.currency_code                         nrm_currency_code
      , r.phone_code                            nrm_phone_code
      , r.tax_id_type                           nrm_tax_id_type
      , r.country_name                          nrm_country_name
      , t.business_unit                         primary_business_unit
      , t.business_units                        business_units
      , t.vendor_id
      , t.vendor_name
      , t.country
      , t.country_code
      , t.created_date
      , t.last_purchase_date
      , t.last_payment_date
  FROM cte_supplier                             t
       -- First try: match on country name (higher population)
       LEFT OUTER JOIN
       ref_country_name_mapping                 m_name
          ON  m_name.source_country_name        = UPPER(TRIM(t.country))
       -- Second try: match on country code (fallback)
       LEFT OUTER JOIN
       ref_country_code_mapping                 m_code
          ON  m_code.source_country_code        = NULLIF(UPPER(TRIM(t.country_code)), '')
       -- Join to reference table using: name match > code match > default GB
       LEFT OUTER JOIN
       ref_country                              r
          ON r.country_code                     = COALESCE(m_name.country_code, m_code.country_code, 'GB')
;
