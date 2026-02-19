DROP TABLE IF EXISTS src_fin_customer
;
CREATE TABLE src_fin_customer
    AS
  WITH cte_customer
    AS (
SELECT t.*
  FROM src_fin_customer_raw                     t
 WHERE t.data_rnk = 1
       )
     , cte_customer_rnk
    AS (
SELECT t.*
     , ROW_NUMBER() OVER(ORDER BY t.nrm_customer_name)           rnk
  FROM cte_customer                                      t
       )
SELECT
       'C-' || LPAD(rnk::VARCHAR, 6, '0')                         customer_id
     , r.country_code                                             nrm_country_code
     , r.language_code                                            nrm_language_code
     , r.currency_code                                            nrm_currency_code
     , r.phone_code                                               nrm_phone_code
     , r.tax_id_type                                              nrm_tax_id_type
     , r.country_name                                             nrm_country_name
     , c.*
  FROM cte_customer_rnk                      c
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
       -- Sort Code normalisation
       LEFT OUTER JOIN
       ref_bank_sort_code_prefix_mapping        rbsc
          ON rbsc.sort_code_prefix              = SUBSTR(NULLIF(TRIM(t.eft_bank_code), ''), 1, 2)
;
