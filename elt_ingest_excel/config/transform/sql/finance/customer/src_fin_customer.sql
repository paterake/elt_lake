DROP TABLE IF EXISTS src_fin_customer
;
CREATE TABLE src_fin_customer
    AS
  WITH cte_customer_src
    AS (
-- FA business unit
SELECT 'FA'   AS business_unit, *   FROM fin_customer_debtor_last_3_years_fa
UNION ALL
SELECT 'FA'   AS business_unit, *   FROM fin_customer_debtor_created_date_fa
UNION ALL
SELECT 'FA'   AS business_unit, *   FROM fin_customer_debtor_last_payment_date_fa
UNION ALL
-- NFC business unit
SELECT 'NFC'  AS business_unit, *   FROM fin_customer_debtor_last_3_years_nfc
UNION ALL
SELECT 'NFC'  AS business_unit, *   FROM fin_customer_debtor_created_date_nfc
UNION ALL
SELECT 'NFC'  AS business_unit, *   FROM fin_customer_debtor_last_payment_date_nfc
UNION ALL
-- WNSL business unit
SELECT 'WNSL' AS business_unit, *   FROM fin_customer_debtor_last_3_years_wnsl
UNION ALL
SELECT 'WNSL' AS business_unit, *   FROM fin_customer_debtor_created_date_wnsl
UNION ALL
SELECT 'WNSL' AS business_unit, *   FROM fin_customer_debtor_last_payment_date_wnsl
       )
     , cte_customer_distinct
    AS (
SELECT DISTINCT *
  FROM cte_customer_src
       )
     , cte_customer_rnk
    AS (
SELECT t.*
     , ROW_NUMBER() OVER
       (PARTITION BY business_unit, customer_number
            ORDER BY
              last_payment_date     DESC NULLS LAST
            , last_transaction_date DESC NULLS LAST
            , created_date          DESC NULLS LAST
       ) data_rnk
  FROM cte_customer_distinct                     t
       )
     , cte_customer
    AS (
SELECT *
     , ROW_NUMBER() OVER (ORDER BY business_unit, customer_name, customer_number)  rnk
  FROM cte_customer_rnk
 WHERE data_rnk = 1
       )
SELECT
       'C-' || LPAD(rnk::VARCHAR, 6, '0')                         customer_id
     , CASE
         WHEN NULLIF(UPPER(TRIM(c.customer_name)), '') IS NULL
         THEN c.customer_number
         ELSE TRIM(c.customer_name)
       END                                                        customer_id_name
     , r.country_code                                             nrm_country_code
     , r.language_code                                            nrm_language_code
     , r.currency_code                                            nrm_currency_code
     , r.phone_code                                               nrm_phone_code
     , r.tax_id_type                                              nrm_tax_id_type
     , r.country_name                                             nrm_country_name
     , c.*
  FROM cte_customer                          c
       -- First try: match on country name (higher population)
       LEFT OUTER JOIN
       ref_source_country_name_mapping       m_name
          ON  m_name.source_country_name     = UPPER(TRIM(c.country))
       -- Second try: match on country code (fallback)
       LEFT OUTER JOIN
       ref_source_country_code_mapping       m_code
          ON  m_code.source_country_code     = NULLIF(UPPER(TRIM(c.country_code)), '')
       -- Join to reference table using: name match > code match > default GB
       LEFT OUTER JOIN
       ref_country                           r
          ON r.country_code                  = COALESCE(m_name.country_code, m_code.country_code, 'GB')
;
