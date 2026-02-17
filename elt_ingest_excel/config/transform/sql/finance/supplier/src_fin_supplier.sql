DROP TABLE IF EXISTS src_fin_supplier
;
CREATE TABLE src_fin_supplier
    AS
  WITH cte_supplier_distinct
    AS (
SELECT *
  FROM src_fin_supplier_raw                     t
       )
     , cte_supplier_rnk
    AS (
SELECT t.*
     , ROW_NUMBER() OVER
       (
         PARTITION BY business_unit, nrm_vendor_name
           ORDER BY
              CASE
                        WHEN (
                              last_payment_ts   > TIMESTAMP '1900-01-01'
                           OR last_purchase_ts  > TIMESTAMP '1900-01-01'
                             )
                 THEN 0
                 ELSE 1
              END ASC
                    , created_ts ASC  NULLS LAST
            , CASE
                        WHEN last_payment_ts > TIMESTAMP '1900-01-01'
                        THEN last_payment_ts
                 ELSE NULL
              END DESC NULLS LAST
            , CASE
                        WHEN last_purchase_ts > TIMESTAMP '1900-01-01'
                        THEN last_purchase_ts
                 ELSE NULL
              END DESC NULLS LAST
       )                                        data_rnk
  FROM cte_supplier_distinct                    t
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
      (PARTITION BY nrm_vendor_name
            ORDER BY created_ts DESC NULLS LAST
       ) primary_rnk
  FROM cte_supplier_per_bu                      t
       )
     , cte_supplier_business_units
    AS (
SELECT nrm_vendor_name
     , ARRAY_AGG(DISTINCT business_unit ORDER BY business_unit)  business_units
  FROM cte_supplier_per_bu
 GROUP BY nrm_vendor_name
       )
     , cte_supplier
    AS (
SELECT t.*
     , bu.business_units
     , ROW_NUMBER() OVER (ORDER BY t.nrm_vendor_name)  rnk
  FROM cte_supplier_primary                     t
       INNER JOIN
       cte_supplier_business_units              bu
         ON  bu.nrm_vendor_name                 = t.nrm_vendor_name
 WHERE t.primary_rnk = 1
       )
SELECT
        'S-' || LPAD(rnk::VARCHAR, 6, '0')      supplier_id
      , r.country_code                          nrm_country_code
      , r.language_code                         nrm_language_code
      , r.currency_code                         nrm_currency_code
      , r.phone_code                            nrm_phone_code
      , r.tax_id_type                           nrm_tax_id_type
      , r.country_name                          nrm_country_name
      , COALESCE(scm.supplier_category, 'Services')    nrm_supplier_category
      , t.business_unit                         primary_business_unit
      , t.*
  FROM cte_supplier                             t
       -- First try: match on country name (higher population)
       LEFT OUTER JOIN
       ref_country_name_mapping                 m_name
          ON  m_name.source_country_name        = NULLIF(UPPER(TRIM(t.country)), '')
       -- Second try: match on country code (fallback)
       LEFT OUTER JOIN
       ref_country_code_mapping                 m_code
          ON  m_code.source_country_code        = NULLIF(UPPER(TRIM(t.country_code)), '')
       -- Join to reference table using: name match > code match > default GB
       LEFT OUTER JOIN
       ref_country                              r
          ON  r.country_code                    = COALESCE(NULLIF(m_name.country_code, ''), NULLIF(m_code.country_code, ''), 'GB')
       -- Supplier category normalization
       LEFT OUTER JOIN
       ref_supplier_category_mapping            scm
          ON  scm.source_supplier_category      = NULLIF(UPPER(TRIM(t.vendor_class_id)), '')
;
