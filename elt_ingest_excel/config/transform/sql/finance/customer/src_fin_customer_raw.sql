INSTALL splink_udfs FROM community;
LOAD splink_udfs;

DROP TABLE IF EXISTS src_fin_customer_raw;

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
     , UPPER(COALESCE(NULLIF(UPPER(TRIM(t.customer_name)), ''), NULLIF(TRIM(t.customer_number), ''))) nrm_customer_name_base
     , CASE 
        WHEN UPPER(TRIM(t.post_code)) LIKE '%KNOWN%'
        THEN NULL 
        ELSE COALESCE(
             -- Try to extract a full valid UK postcode (e.g. 'AL5 2LG', 'W1B 5TR' 'AL5, 2LG')
             -- Handles comma separators by replacing them with space first
             -- Normalizes multiple spaces to single space
             NULLIF(
                 REGEXP_REPLACE(
                     REGEXP_EXTRACT(UPPER(REPLACE(t.post_code, ',', ' ')), '([A-Z]{1,2}[0-9][0-9A-Z]?\s*[0-9][A-Z]{2})'),
                     '\s+', ' ', 'g'
                 ),
                 ''
             ),
             -- Fallback: Just take the first part (e.g. 'AL5' from 'AL5, Herts') if regex failed
             NULLIF(UPPER(TRIM(SPLIT_PART(t.post_code, ',', 1))), '')
        )
       END                                                                                            nrm_postal_code_clean
     , t.*
  FROM cte_customer_src                      t
       )
     , cte_customer_nrm
    AS (
SELECT 
       CASE
         -- Full postcodes are always 5, 6, or 7 characters (cleaned)
         WHEN LENGTH(REGEXP_REPLACE(UPPER(TRIM(t.nrm_postal_code_clean)), '\s', '', 'g')) IN (5, 6, 7)
         THEN REGEXP_REPLACE(REGEXP_REPLACE(UPPER(TRIM(t.nrm_postal_code_clean)), '\s', '', 'g'), '(.+)(.{3})$', '\1 \2')
         -- Partials (2-4 chars) or Garbage (8+ chars) remain unchanged (cleaned)
         ELSE REGEXP_REPLACE(UPPER(TRIM(t.nrm_postal_code_clean)), '\s', '', 'g')
       END                                                                                            nrm_postal_code
       -- Clean Name: Remove dots, Normalize 'FOOTBALL CLUB' -> 'FC', then strip trailing suffixes (Limited, etc)
     , TRIM(REGEXP_REPLACE(
           REPLACE(
                REPLACE(
                    REPLACE(
                        REPLACE(UPPER(unaccent(t.nrm_customer_name_base)), '.', ''),
                        'WOMEN''S', 'WOMEN'
                    ),
                    'WOMENS', 'WOMEN'
                ),
                'FOOTBALL CLUB', 'FC'
            ),
           '(\s+|^)((LIMITED|LTD|COMPANY|PLC|LLP|INC)\s*)+$', ''
       ))                                                                                             nrm_customer_name
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
     , cte_customer_rank
    AS (
SELECT 
       ROW_NUMBER() OVER
       (
         PARTITION BY 
                   t.nrm_customer_name
                 , t.nrm_customer_number
             ORDER BY
                   t.nrm_created_date           ASC  NULLS LAST
                 , t.nrm_last_payment_date      DESC NULLS LAST
                 , t.nrm_last_transaction_date  DESC NULLS LAST
       )                                                           data_rnk
     , t.* 
  FROM cte_customer_nrm                t
       )
     , cte_customer_addr_clean 
    AS (
SELECT t.*
       , LIST_DISTINCT(LIST_FILTER([
             NULLIF(NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(REGEXP_REPLACE(t.address_1, '[\"`<>|;{}]', '', 'g'), '\\s+', ' ', 'g'), ',+$', '')), '[Not Known]'), '')
           , NULLIF(NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(REGEXP_REPLACE(t.address_2, '[\"`<>|;{}]', '', 'g'), '\\s+', ' ', 'g'), ',+$', '')), '[Not Known]'), '')
           , NULLIF(NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(REGEXP_REPLACE(t.address_3, '[\"`<>|;{}]', '', 'g'), '\\s+', ' ', 'g'), ',+$', '')), '[Not Known]'), '')
         ], x -> x IS NOT NULL))                                  addr_unique_list
    FROM cte_customer_rank             t
       )
SELECT 
       r.country_code                                             nrm_country_code
     , r.language_code                                            nrm_language_code
     , r.currency_code                                            nrm_currency_code
     , r.phone_code                                               nrm_phone_code
     , r.tax_id_type                                              nrm_tax_id_type
     , r.country_name                                             nrm_country_name
     , COALESCE(rx.instance, rxo.instance)                        nrm_region
     , SPLIT_PART(
       CASE
        WHEN r0.post_town           IS NOT NULL
        THEN r0.post_town
        WHEN r3.town_city_name      IS NOT NULL
        THEN r3.town_city_name
        WHEN r4.town_city_name      IS NOT NULL
        THEN r4.town_city_name
        ELSE NULLIF(TRIM(c.city), '')
       END
       , ',', 1)                                                  nrm_city
     , c.addr_unique_list[1]                                      nrm_address_line_1
     , c.addr_unique_list[2]                                      nrm_address_line_2
     , c.addr_unique_list[3]                                      nrm_address_line_3
     , CAST(NULL AS STRING)                                       nrm_address_line_4
     , NULLIF(TRIM(UPPER(c.payment_terms_id)), '')                nrm_payment_terms_id
     , NULLIF(TRIM(UPPER(c.tax_schedule_id)), '')                 nrm_tax_schedule_id
     , NULLIF(TRIM(UPPER(c.tax_registration_number)), '')         nrm_tax_registration_number
     , COALESCE(NULLIF(TRIM(UPPER(c.address_code)), ''), 'MAIN')  nrm_address_code
     , c.*
 FROM cte_customer_addr_clean                   c
       -- First try: match on country name (higher population)
       LEFT OUTER JOIN
       ref_source_country_name_mapping          m_name
          ON  m_name.source_country_name        = UPPER(TRIM(c.country))
       -- Second try: match on country code (fallback)
       LEFT OUTER JOIN
       ref_source_country_code_mapping          m_code
          ON  m_code.source_country_code        = NULLIF(UPPER(TRIM(c.country_code)), '')
       -- Join to reference table using: name match > code match > default GB
       LEFT OUTER JOIN
       ref_country                              r
          ON r.country_code                     = COALESCE(m_name.country_code, m_code.country_code, 'GB')          
       -- Address handling
       LEFT OUTER JOIN
       ref_post_code_district                   r0
          ON UPPER(TRIM(c.nrm_postal_code))     LIKE r0.postcode || ' %' 
       LEFT OUTER JOIN
       ref_post_code_workday_region             r01
          ON UPPER(TRIM(r01.post_code_region))  = UPPER(TRIM(r0.region))
       LEFT OUTER JOIN 
       ref_workday_country_state_region         r1
         ON r1.country                          = r.country_name
        AND UPPER(TRIM(r1.instance))            = UPPER(TRIM(c.county))
       LEFT OUTER JOIN 
       ref_workday_country_state_region         r2
         ON r2.country                          = r.country_name
        AND UPPER(TRIM(r2.instance))            = UPPER(TRIM(c.city))   
       LEFT OUTER JOIN
       ref_country_county_state_town_mapping    r3
         ON r3.country_code                     = r.country_code
        AND UPPER(TRIM(r3.town_city_name))      = UPPER(TRIM(c.county))
       LEFT OUTER JOIN
       ref_country_county_state_town_mapping    r4
         ON r4.country_code                     = r.country_code
        AND UPPER(TRIM(r4.town_city_name))      = UPPER(TRIM(c.city))       
       LEFT OUTER JOIN 
       ref_workday_country_state_region         rx
         ON rx.country                          = r.country_name
        AND UPPER(TRIM(rx.instance))            = UPPER(TRIM(
                                                  CASE
                                                   WHEN r0.region             IS NOT NULL THEN COALESCE(UPPER(TRIM(r01.workday_region)), UPPER(TRIM(r0.region)))
                                                   WHEN r1.instance           IS NOT NULL THEN UPPER(TRIM(r1.instance))
                                                   WHEN r2.instance           IS NOT NULL THEN UPPER(TRIM(r2.instance)) 
                                                   WHEN r3.county_state_name  IS NOT NULL THEN UPPER(TRIM(r3.county_state_name))
                                                   WHEN r4.county_state_name  IS NOT NULL THEN UPPER(TRIM(r4.county_state_name))
                                                   ELSE NULLIF(UPPER(TRIM(c.county)), '')
                                                  END))
       LEFT OUTER JOIN 
       ref_workday_country_state_region         rxo
         ON rxo.country                         = r.country_name
        AND UPPER(TRIM(rxo.instance))           = UPPER(TRIM(
                                                  CASE
                                                   WHEN r0.region             IS NOT NULL THEN COALESCE(UPPER(TRIM(r01.workday_region)), UPPER(TRIM(r0.region)))
                                                   WHEN r1.instance           IS NOT NULL THEN UPPER(TRIM(r1.instance))
                                                   WHEN r2.instance           IS NOT NULL THEN UPPER(TRIM(r2.instance)) 
                                                   WHEN r3.county_state_name  IS NOT NULL THEN UPPER(TRIM(r3.county_state_name))
                                                   WHEN r4.county_state_name  IS NOT NULL THEN UPPER(TRIM(r4.county_state_name))
                                                   ELSE NULLIF(UPPER(TRIM(c.county)), '')
                                                  END || '(obsolete)'))
;
