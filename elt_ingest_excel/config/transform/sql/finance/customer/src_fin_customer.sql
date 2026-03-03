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
     , rx.instance                                                nrm_region
     , CASE
        WHEN r0.city                IS NOT NULL
        THEN r0.city
        WHEN r3.town_city_name      IS NOT NULL
        THEN r3.town_city_name
        WHEN r4.town_city_name      IS NOT NULL
        THEN r4.town_city_name
        ELSE NULLIF(TRIM(c.city), '')
       END                                                        nrm_city
     , COALESCE(
         NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(c.address_1, '[\"`<>|;{}]', '', 'g'), '\\s+', ' ', 'g')), ''),
         NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(c.address_2, '[\"`<>|;{}]', '', 'g'), '\\s+', ' ', 'g')), ''),
         NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(c.address_3, '[\"`<>|;{}]', '', 'g'), '\\s+', ' ', 'g')), '')
       )                                                          nrm_address_line_1
     , NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(c.address_2, '[\"`<>|;{}]', '', 'g'), '\\s+', ' ', 'g')), '')
                                                                  nrm_address_line_2
     , NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(c.address_3, '[\"`<>|;{}]', '', 'g'), '\\s+', ' ', 'g')), '')
                                                                  nrm_address_line_3
     , NULL                                                       nrm_address_line_4
     , NULLIF(TRIM(UPPER(c.post_code)), '')                       nrm_postal_code
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
       -- Address handling
       LEFT OUTER JOIN
       ref_post_code_county                     r0
          ON UPPER(TRIM(c.post_code))           LIKE r0.postcode || ' %' 
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
        AND UPPER(TRIM(rx.instance))            = CASE
                                                   WHEN r0.county             IS NOT NULL THEN UPPER(TRIM(r0.county))
                                                   WHEN r1.instance           IS NOT NULL THEN UPPER(TRIM(r1.instance))
                                                   WHEN r2.instance           IS NOT NULL THEN UPPER(TRIM(r2.instance)) 
                                                   WHEN r3.county_state_name  IS NOT NULL THEN UPPER(TRIM(r3.county_state_name))
                                                   WHEN r4.county_state_name  IS NOT NULL THEN UPPER(TRIM(r4.county_state_name))
                                                   ELSE NULLIF(UPPER(TRIM(c.county)), '')
                                                  END
;
