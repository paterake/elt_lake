DROP TABLE IF EXISTS src_fin_supplier
;
CREATE TABLE src_fin_supplier
    AS
  WITH cte_supplier
    AS (
SELECT t.*
  FROM src_fin_supplier_raw                              t
 WHERE t.data_rnk = 1
       )
     , cte_supplier_rnk
    AS (
SELECT t.*
     , ROW_NUMBER() OVER(ORDER BY t.nrm_vendor_name)   rnk
  FROM cte_supplier                                      t
       )
SELECT
        'S-' || LPAD(rnk::VARCHAR, 6, '0')               supplier_id
      , r.country_code                                   nrm_country_code
      , r.language_code                                  nrm_language_code
      , r.currency_code                                  nrm_currency_code
      , r.phone_code                                     nrm_phone_code
      , r.tax_id_type                                    nrm_tax_id_type
      , r.country_name                                   nrm_country_name
      , m_county.county_state_name                       nrm_county
      , COALESCE(scm.supplier_category, 'Services')      nrm_supplier_category
      , rbcs.
      , t.*
  FROM cte_supplier_rnk                         t
       -- First try: match on country name (higher population)
       LEFT OUTER JOIN
       ref_source_country_name_mapping          m_name
          ON  m_name.source_country_name        = NULLIF(UPPER(TRIM(t.country)), '')
       -- Second try: match on country code (fallback)
       LEFT OUTER JOIN
       ref_source_country_code_mapping          m_code
          ON  m_code.source_country_code        = NULLIF(UPPER(TRIM(t.country_code)), '')
       -- Join to reference table using: name match > code match > default GB
       LEFT OUTER JOIN
       ref_country                              r
          ON  r.country_code                    = COALESCE(NULLIF(m_name.country_code, ''), NULLIF(m_code.country_code, ''), 'GB')
       -- County mappings.   
       LEFT OUTER JOIN
       ref_country_county_state_mapping         m_county
          ON m_county.country_code             = r.country_code
         AND UPPER(m_county.county_state_name) = NULLIF(UPPER(TRIM(t.county)), '')
       -- Supplier category normalization
       LEFT OUTER JOIN
       ref_supplier_category_mapping            scm
          ON scm.source_supplier_category      = NULLIF(UPPER(TRIM(t.vendor_class_id)), '')
       -- Sort Code normalisation
       LEFT OUTER JOIN
       ref_bank_sort_code_mapping               rbsc
          ON rbsc.sort_code_prefix              = SUBSTR(NULLIF(TRIM(eft_bank_code), ''), 1, 2)
;
