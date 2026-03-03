DROP TABLE IF EXISTS src_fin_supplier_v2
;
CREATE TABLE src_fin_supplier_v2
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
        'S-' || LPAD(rnk::VARCHAR, 6, '0')                                             supplier_id
      , r.country_code                                                                 nrm_country_code
      , r.language_code                                                                nrm_language_code
      , r.currency_code                                                                nrm_currency_code
      , r.phone_code                                                                   nrm_phone_code
      , r.tax_id_type                                                                  nrm_tax_id_type
      , r.country_name                                                                 nrm_country_name
      , COALESCE(scm.supplier_category, 'Consulting Services and Professional Fees')   nrm_supplier_category
      , NULLIF(TRIM(t.eft_bank_code), '')                                              nrm_bank_sort_code
      , rbsc.bank_name_primary                                                         nrm_bank_name
      , rx.instance                                                                    nrm_region
      , CASE
         WHEN r0.city                IS NOT NULL
         THEN r0.city
         WHEN r3.town_city_name      IS NOT NULL
         THEN r3.town_city_name
         WHEN r4.town_city_name      IS NOT NULL
         THEN r4.town_city_name
         ELSE NULLIF(TRIM(s.city), '')
        END                                                                            nrm_city
      , TRIM(REGEXP_REPLACE(REGEXP_REPLACE(t.address_1, '[\"`<>|;{}]', '', 'g'), '\\s+', ' ', 'g'))
                                                                                       nrm_address_line_1
      , NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(t.address_2, '[\"`<>|;{}]', '', 'g'), '\\s+', ' ', 'g')), '')
                                                                                       nrm_address_line_2
      , NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(t.address_3, '[\"`<>|;{}]', '', 'g'), '\\s+', ' ', 'g')), '')
                                                                                       nrm_address_line_3
      , NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(t.addressline_4, '[\"`<>|;{}]', '', 'g'), '\\s+', ' ', 'g')), '')
                                                                                       nrm_address_line_4
      , NULLIF(TRIM(UPPER(t.post_code)), '')                                           nrm_postal_code
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
        -- Supplier category normalization
        LEFT OUTER JOIN
        ref_supplier_category_mapping            scm
           ON scm.source_supplier_category      = NULLIF(UPPER(TRIM(t.vendor_class_id)), '')
        -- Sort Code normalisation
        LEFT OUTER JOIN
        ref_bank_sort_code_prefix_mapping        rbsc
          ON rbsc.sort_code_prefix              = SUBSTR(NULLIF(TRIM(t.eft_bank_code), ''), 1, 2)
        -- Address handling
        LEFT OUTER JOIN
        ref_post_code_county                     r0
          ON UPPER(TRIM(t.post_code))           LIKE r0.postcode || ' %' 
        LEFT OUTER JOIN 
        ref_workday_country_state_region         r1
          ON r1.country                          = r.country_name
         AND UPPER(TRIM(r1.instance))            = UPPER(TRIM(t.county))
        LEFT OUTER JOIN 
        ref_workday_country_state_region         r2
          ON r2.country                          = r.country_name
         AND UPPER(TRIM(r2.instance))            = UPPER(TRIM(t.city))
        LEFT OUTER JOIN
        ref_country_county_state_town_mapping    r3
          ON r3.country_code                     = r.country_code
         AND UPPER(TRIM(r3.town_city_name))      = UPPER(TRIM(t.county))       
        LEFT OUTER JOIN
        ref_country_county_state_town_mapping    r4
          ON r4.country_code                     = r.country_code
         AND UPPER(TRIM(r4.town_city_name))      = UPPER(TRIM(t.city))
        LEFT OUTER JOIN 
        ref_workday_country_state_region         rx
          ON rx.country                          = r.country_name
         AND UPPER(TRIM(rx.instance))            = CASE
                                                    WHEN r0.county             IS NOT NULL THEN UPPER(TRIM(r0.county))
                                                    WHEN r1.instance           IS NOT NULL THEN UPPER(TRIM(r1.instance))
                                                    WHEN r2.instance           IS NOT NULL THEN UPPER(TRIM(r2.instance)) 
                                                    WHEN r3.county_state_name  IS NOT NULL THEN UPPER(TRIM(r3.county_state_name))
                                                    WHEN r4.county_state_name  IS NOT NULL THEN UPPER(TRIM(r4.county_state_name))
                                                    ELSE NULLIF(UPPER(TRIM(t.county)), '')
                                                   END
  WHERE NULLIF(TRIM(t.payment_terms_id), '')    IS NOT NULL
;
