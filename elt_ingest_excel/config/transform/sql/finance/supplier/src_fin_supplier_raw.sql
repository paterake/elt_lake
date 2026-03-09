INSTALL splink_udfs FROM community
;
LOAD splink_udfs
;

DROP TABLE IF EXISTS src_fin_supplier_raw
;
CREATE TABLE src_fin_supplier_raw
    AS
  WITH cte_supplier_src
    AS (
SELECT t.company business_unit, t.* FROM fin_supplier_creditor_no_activity_1_year      t
UNION ALL
SELECT t.company business_unit, t.* FROM fin_supplier_creditor_activity_2_years        t
       )
     , cte_supplier_base
    AS (
SELECT DISTINCT
       TRIM(t.vendor_id)                                                                              nrm_supplier_number
     , UPPER(COALESCE(NULLIF(UPPER(TRIM(t.vendor_id)), ''), NULLIF(TRIM(t.vendor_name), '')))         nrm_supplier_name_base
     , CASE 
        WHEN UPPER(TRIM(t.post_code)) LIKE '%KNOWN%' OR TRIM(t.post_code) = '-'
        THEN NULL 
        ELSE COALESCE(
             -- Try to extract a full valid UK postcode (e.g. 'AL5 2LG', 'W1B 5TR', 'IM3-1AD')
             -- Handles comma and hyphen separators by replacing them with space first
             -- Normalizes multiple spaces to single space
             NULLIF(
                 REGEXP_REPLACE(
                     REGEXP_EXTRACT(UPPER(REGEXP_REPLACE(t.post_code, '[, -]', ' ', 'g')), '([A-Z]{1,2}[0-9][0-9A-Z]?\s*[0-9][A-Z]{2})'),
                     '\s+', ' ', 'g'
                 ),
                 ''
             ),
             -- Fallback: Just take the first part (e.g. 'AL5' from 'AL5, Herts') if regex failed
             -- Also replace hyphen with space in the fallback to handle 'IM2- 1AD' if regex fails (though regex should catch it)
             NULLIF(TRIM(REPLACE(UPPER(TRIM(SPLIT_PART(t.post_code, ',', 1))), '-', ' ')), '')
        )
       END                                                                                            nrm_postal_code_clean
     , t.*
  FROM cte_supplier_src                t
       )
     , cte_supplier_nrm
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
                        REPLACE(UPPER(unaccent(t.nrm_supplier_name_base)), '.', ''),
                        'WOMEN''S', 'WOMEN'
                    ),
                    'WOMENS', 'WOMEN'
                ),
                'FOOTBALL CLUB', 'FC'
            ),
           '(\s+|^)((LIMITED|LTD|COMPANY|PLC|LLP|INC)\s*)+$', ''
       ))                                                                                             nrm_supplier_name
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
          TRY_STRPTIME(NULLIF(TRIM(t.last_purchase_date    ), ''), '%Y-%m-%d %H:%M:%S')
        , TRY_STRPTIME(NULLIF(TRIM(t.last_purchase_date    ), ''), '%Y-%m-%d')
        , TRY_STRPTIME(NULLIF(TRIM(t.last_purchase_date    ), ''), '%d-%m-%Y')
       )                                                                                              nrm_last_purchase_date
     , mbu.target_value                                                                               nrm_business_unit
     , t.*
  FROM cte_supplier_base                     t
       INNER JOIN
       ref_source_business_unit_mapping      mbu
          ON UPPER(mbu.source_value)         = UPPER(TRIM(t.business_unit))
       )
     , cte_supplier_addr_clean 
    AS (
SELECT t.*
     , LIST_DISTINCT(LIST_FILTER([
         NULLIF(NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(REGEXP_REPLACE(t.address_1    , '[\"`<>|;{}]', '', 'g'), '\\s+', ' ', 'g'), ',+$', '')), '[Not Known]'), '')
       , NULLIF(NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(REGEXP_REPLACE(t.address_2    , '[\"`<>|;{}]', '', 'g'), '\\s+', ' ', 'g'), ',+$', '')), '[Not Known]'), '')
       , NULLIF(NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(REGEXP_REPLACE(t.address_3    , '[\"`<>|;{}]', '', 'g'), '\\s+', ' ', 'g'), ',+$', '')), '[Not Known]'), '')
       , NULLIF(NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(REGEXP_REPLACE(t.addressline_4, '[\"`<>|;{}]', '', 'g'), '\\s+', ' ', 'g'), ',+$', '')), '[Not Known]'), '')
       ], x -> x IS NOT NULL))                                           addr_unique_list
  FROM cte_supplier_nrm                      t
       )
     , cte_supplier_clean
    AS (
SELECT 
       r.country_code                                                               nrm_country_code
     , r.language_code                                                              nrm_language_code
     , r.currency_code                                                              nrm_currency_code
     , r.phone_code                                                                 nrm_phone_code
     , r.tax_id_type                                                                nrm_tax_id_type
     , r.country_name                                                               nrm_country_name
     , COALESCE(scm.supplier_category, 'Consulting Services and Professional Fees') nrm_supplier_category
     , COALESCE(rx.instance, rxo.instance)                                          nrm_region
     , SPLIT_PART(
       CASE
        WHEN r0.post_town           IS NOT NULL
        THEN r0.post_town
        WHEN r3.town_city_name      IS NOT NULL
        THEN r3.town_city_name
        WHEN r4.town_city_name      IS NOT NULL
        THEN r4.town_city_name
        ELSE NULLIF(TRIM(t.city), '')
       END
       , ',', 1)                                                                    nrm_city
     , t.addr_unique_list[1]                                                        nrm_address_line_1
     , t.addr_unique_list[2]                                                        nrm_address_line_2
     , t.addr_unique_list[3]                                                        nrm_address_line_3
     , t.addr_unique_list[4]                                                        nrm_address_line_4
     , COALESCE(NULLIF(TRIM(UPPER(t.vendor_address_code_primary)), ''), 'MAIN')     nrm_address_code
     , NULLIF(UPPER(TRIM(t.tax_schedule_id)), '')                                   nrm_tax_schedule_id
     , NULLIF(UPPER(TRIM(t.tax_id_number  )), '')                                   nrm_tax_id_number
     , pt.workday_payment_terms                                                     nrm_payment_terms_id
     , rbsc.bank_name_primary                                                       nrm_bank_name
     , NULLIF(TRIM(t.eft_bank_code), '')                                            nrm_bank_sort_code
     , COALESCE(NULLIF(TRIM(t.vendor_check_name), ''), t.nrm_supplier_name)         nrm_bank_account_name
     , NULLIF(TRIM(REPLACE(t.eft_bank_account, ' ', '')), '')                       nrm_bank_account_number
     , CASE
         WHEN r.country_code IN ('GB', 'IE', 'FR', 'DE', 'ES', 'IT', 'NL', 'BE', 'PT', 'AT', 'SE', 'DK', 'FI')
         THEN TRIM(REPLACE(REPLACE(t.eft_bank_code, ' ', ''), '-', ''))
         WHEN r.country_code = 'US'
         THEN TRIM(REPLACE(REPLACE(t.eft_transit_routing_no, ' ', ''), '-', ''))
         ELSE TRIM(REPLACE(REPLACE(t.eft_bank_code, ' ', ''), '-', ''))
       END                                                                          nrm_bank_code_routing_number
     , NULLIF(TRIM(REPLACE(REPLACE(UPPER(t.iban), ' ', ''), '-', '')), '')          nrm_bank_iban
     , NULLIF(TRIM(UPPER(t.swift_address)), '')                                     nrm_bank_swift_code
     , NULLIF(TRIM(t.building_society_roll_no), '')                                 nrm_bank_roll_number
     , NULLIF(TRIM(t.eft_bank_check_digit), '')                                     nrm_bank_check_digit
     , NULLIF(TRIM(t.eft_bank_branch_code), '')                                     nrm_bank_branch_id
     , NULLIF(TRIM(t.eft_bank_branch), '')                                          nrm_bank_branch_name
     , NULLIF(TRIM(t.eft_transfer_method), '')                                      nrm_bank_transfer_method
     , t.*
  FROM cte_supplier_addr_clean                  t
       -- First try: match on country name (higher population)
       LEFT OUTER JOIN
       ref_source_country_name_mapping          m_name
         ON  m_name.source_country_name         = UPPER(TRIM(t.country))
       -- Second try: match on country code (fallback)
       LEFT OUTER JOIN
       ref_source_country_code_mapping          m_code
         ON  m_code.source_country_code         = NULLIF(UPPER(TRIM(t.country_code)), '')
       -- Join to reference table using: name match > code match > default GB
       LEFT OUTER JOIN
       ref_country                              r
         ON r.country_code                      = COALESCE(m_name.country_code, m_code.country_code, 'GB')          
       -- Supplier category normalization
       LEFT OUTER JOIN
       ref_supplier_category_mapping            scm
         ON scm.source_supplier_category        = NULLIF(UPPER(TRIM(t.vendor_class_id)), '')
       -- Payment Terms normalization
       LEFT OUTER JOIN
       ref_source_payment_terms                 pt
         ON  UPPER(pt.source_payment_terms)     = UPPER(TRIM(t.payment_terms_id))
       -- Sort Code normalisation
       LEFT OUTER JOIN
        ref_bank_sort_code_prefix_mapping       rbsc
          ON rbsc.sort_code_prefix              = SUBSTR(NULLIF(TRIM(t.eft_bank_code), ''), 1, 2)
       -- Address handling
       LEFT OUTER JOIN
       ref_post_code_district                   r0
          ON (
               UPPER(TRIM(t.nrm_postal_code))   LIKE r0.postcode || ' %'  -- Matches 'MK19 5AH' to 'MK19'
            OR UPPER(TRIM(t.nrm_postal_code))   =    r0.postcode          -- Matches 'MK19'     to 'MK19'
             ) 
       LEFT OUTER JOIN
       ref_post_code_workday_region             r01
          ON UPPER(TRIM(r01.post_code_region))  = UPPER(TRIM(r0.region))
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
        AND UPPER(TRIM(rx.instance))            = UPPER(TRIM(
                                                  CASE
                                                   WHEN r0.region             IS NOT NULL THEN COALESCE(UPPER(TRIM(r01.workday_region)), UPPER(TRIM(r0.region)))
                                                   WHEN r1.instance           IS NOT NULL THEN UPPER(TRIM(r1.instance))
                                                   WHEN r2.instance           IS NOT NULL THEN UPPER(TRIM(r2.instance)) 
                                                   WHEN r3.county_state_name  IS NOT NULL THEN UPPER(TRIM(r3.county_state_name))
                                                   WHEN r4.county_state_name  IS NOT NULL THEN UPPER(TRIM(r4.county_state_name))
                                                   ELSE NULLIF(UPPER(TRIM(t.county)), '')
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
                                                   ELSE NULLIF(UPPER(TRIM(t.county)), '')
                                                  END || '(obsolete)'))
       )
SELECT 
       ROW_NUMBER() OVER
       (
         PARTITION BY
                   t.nrm_supplier_name
                 , t.nrm_supplier_number
           ORDER BY
                   CASE
                     WHEN t.nrm_bank_name IS NOT NULL
                     THEN 0
                     ELSE 1
                   END ASC NULLS LAST
                 , CASE
                     WHEN t.nrm_bank_account_number IS NOT NULL
                     THEN 0
                     ELSE 1
                   END ASC NULLS LAST
                 , t.nrm_created_date           ASC  NULLS LAST
                 , t.nrm_last_payment_date      DESC NULLS LAST
                 , t.nrm_last_purchase_date     DESC NULLS LAST
       )                                                                   data_rnk
     , t.*
  FROM cte_supplier_clean              t
;
