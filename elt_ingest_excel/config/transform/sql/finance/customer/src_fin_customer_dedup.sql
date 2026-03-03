
INSTALL splink_udfs FROM community;
LOAD splink_udfs;

DROP TABLE IF EXISTS src_fin_customer_dedup;

CREATE TABLE src_fin_customer_dedup AS
WITH normalized_data AS (
    SELECT t.*
         -- Address Normalization (Extracted from workday_customer_address.sql)
         , rx.instance                                                            nrm_region
         , CASE
            WHEN r0.city                IS NOT NULL THEN r0.city
            WHEN r3.town_city_name      IS NOT NULL THEN r3.town_city_name
            WHEN r4.town_city_name      IS NOT NULL THEN r4.town_city_name
            ELSE NULLIF(TRIM(t.city), '')
           END                                                                    nrm_city
         , COALESCE(
             NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(t.address_1, '["`<>|;{}]', '', 'g'), '\s+', ' ', 'g')), ''),
             NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(t.address_2, '["`<>|;{}]', '', 'g'), '\s+', ' ', 'g')), ''),
             NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(t.address_3, '["`<>|;{}]', '', 'g'), '\s+', ' ', 'g')), '')
           )                                                                      nrm_address_line_1
         , NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(t.address_2, '["`<>|;{}]', '', 'g'), '\s+', ' ', 'g')), '') nrm_address_line_2
         , NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(t.address_3, '["`<>|;{}]', '', 'g'), '\s+', ' ', 'g')), '') nrm_address_line_3
         , NULLIF(TRIM(UPPER(t.post_code)), '')                                   nrm_postal_code
    FROM src_fin_customer_raw t
       -- Address Reference Joins
       LEFT OUTER JOIN
       ref_post_code_county                     r0
          ON UPPER(TRIM(t.post_code))           LIKE r0.postcode || ' %' 
       LEFT OUTER JOIN 
       ref_workday_country_state_region         r1
         ON r1.country                          = t.nrm_country_name
        AND UPPER(TRIM(r1.instance))            = UPPER(TRIM(t.county))
       LEFT OUTER JOIN 
       ref_workday_country_state_region         r2
         ON r2.country                          = t.nrm_country_name
        AND UPPER(TRIM(r2.instance))            = UPPER(TRIM(t.city))   
       LEFT OUTER JOIN
       ref_country_county_state_town_mapping    r3
         ON r3.country_code                     = t.nrm_country_code
        AND UPPER(TRIM(r3.town_city_name))      = UPPER(TRIM(t.county))
       LEFT OUTER JOIN
       ref_country_county_state_town_mapping    r4
         ON r4.country_code                     = t.nrm_country_code
        AND UPPER(TRIM(r4.town_city_name))      = UPPER(TRIM(t.city))       
       LEFT OUTER JOIN 
       ref_workday_country_state_region         rx
         ON rx.country                          = t.nrm_country_name
        AND UPPER(TRIM(rx.instance))            = CASE
                                                   WHEN r0.county             IS NOT NULL THEN UPPER(TRIM(r0.county))
                                                   WHEN r1.instance           IS NOT NULL THEN UPPER(TRIM(r1.instance))
                                                   WHEN r2.instance           IS NOT NULL THEN UPPER(TRIM(r2.instance)) 
                                                   WHEN r3.county_state_name  IS NOT NULL THEN UPPER(TRIM(r3.county_state_name))
                                                   WHEN r4.county_state_name  IS NOT NULL THEN UPPER(TRIM(r4.county_state_name))
                                                   ELSE NULLIF(UPPER(TRIM(t.county)), '')
                                                  END
    WHERE t.data_rnk = 1
),
scored_data AS (
    SELECT t.*
         , UPPER(TRIM(t.nrm_customer_name)) as orig_name
         , UPPER(REGEXP_REPLACE(t.nrm_postal_code, '\s+', '', 'g')) as clean_postcode
         -- Clean Name: Remove generic suffixes
         , UPPER(REGEXP_REPLACE(REGEXP_REPLACE(t.nrm_customer_name, '[^a-zA-Z0-9\s]', '', 'g'), '\b(LTD|LIMITED|PLC|GROUP|HOLDINGS|FC|FOOTBALL|CLUB|ASSOCIATION)\b', '', 'gi')) as clean_name
         -- Check for distinct entities to keep separate
         , CASE WHEN REGEXP_MATCHES(t.nrm_customer_name, '\b(WOMEN|WOMENS|LADIES|FOUNDATION|TRUST|COMMUNITY)\b', 'i') THEN 1 ELSE 0 END as is_distinct_entity
         -- Categorize Entity Type
         , CASE 
             WHEN REGEXP_MATCHES(t.nrm_customer_name, '\b(WOMEN|WOMENS|LADIES)\b', 'i') THEN 'WOMEN'
             WHEN REGEXP_MATCHES(t.nrm_customer_name, '\b(FOUNDATION|TRUST|COMMUNITY)\b', 'i') THEN 'FOUNDATION'
             ELSE 'MAIN'
           END as entity_type
         -- Calculate Completeness Score (Using Normalized Fields)
         , (
             (CASE WHEN NULLIF(TRIM(t.payment_terms_id), '') IS NOT NULL THEN 50 ELSE 0 END) +
             (CASE WHEN NULLIF(TRIM(t.tax_schedule_id), '') IS NOT NULL THEN 40 ELSE 0 END) +
             (CASE WHEN NULLIF(TRIM(t.tax_registration_number), '') IS NOT NULL THEN 30 ELSE 0 END) +
             (CASE WHEN t.nrm_address_line_1 IS NOT NULL THEN 20 ELSE 0 END) +
             (CASE WHEN t.nrm_postal_code IS NOT NULL THEN 20 ELSE 0 END) +
             (CASE WHEN t.nrm_city IS NOT NULL THEN 10 ELSE 0 END) +
             (CASE WHEN NULLIF(TRIM(t.country), '') IS NOT NULL THEN 10 ELSE 0 END) +
             (CASE WHEN NULLIF(TRIM(t.nrm_currency_code), '') IS NOT NULL THEN 10 ELSE 0 END)
           ) as completeness_score
    FROM normalized_data t
),
grouped_keys AS (
    SELECT t.*
         , COALESCE(
             -- Rule: Entity Type + Soundex(Clean Name) + Postcode -> Merge
             CASE WHEN clean_name IS NOT NULL AND LENGTH(clean_name) > 2 AND clean_postcode IS NOT NULL AND LENGTH(clean_postcode) > 4
                  THEN 'MERGE:' || entity_type || ':' || SOUNDEX(clean_name) || ':' || clean_postcode
             END,
             -- Rule 3: Entity Type + Clean Name Prefix Match (for multi-site entities) -> Merge
             CASE WHEN clean_name IS NOT NULL AND LENGTH(clean_name) > 10 AND entity_type IN ('WOMEN', 'FOUNDATION', 'TRUST')
                  THEN 'MERGE_NAME:' || entity_type || ':' || SUBSTR(clean_name, 1, 15)
             END,
             -- Fallback: Treat as unique
             'ORIG:' || t.nrm_customer_number
           ) as dedup_key
    FROM scored_data t
),
ranked_groups AS (
    SELECT t.*
         , ROW_NUMBER() OVER (
             PARTITION BY dedup_key 
             ORDER BY 
                 completeness_score DESC,
                 data_rnk ASC,
                 nrm_customer_number DESC
           ) as group_rnk
    FROM grouped_keys t
),
aggregated_contacts AS (
    SELECT dedup_key
         , STRING_AGG(DISTINCT NULLIF(TRIM(email_to_address), ''), '; ') as combined_emails
    FROM grouped_keys
    GROUP BY dedup_key
),
final_deduped AS (
    SELECT m.*
         , a.combined_emails
    FROM ranked_groups m
    JOIN aggregated_contacts a ON m.dedup_key = a.dedup_key
    WHERE m.group_rnk = 1
),
cte_customer_rnk AS (
    SELECT t.*
         , ROW_NUMBER() OVER(ORDER BY t.nrm_customer_name) as rnk
    FROM final_deduped t
)
SELECT
        'C-' || LPAD(rnk::VARCHAR, 6, '0')                                             customer_id
      , r.country_code                                                                 nrm_country_code
      , r.language_code                                                                nrm_language_code
      , r.currency_code                                                                nrm_currency_code
      , r.phone_code                                                                   nrm_phone_code
      , r.tax_id_type                                                                  nrm_tax_id_type
      , r.country_name                                                                 nrm_country_name
      , t.nrm_customer_number                                                          nrm_customer_number
      , t.*
      , t.combined_emails                                                              email_to_address
   FROM cte_customer_rnk                         t
        LEFT OUTER JOIN
        ref_source_country_name_mapping          m_name
           ON  m_name.source_country_name        = NULLIF(UPPER(TRIM(t.country)), '')
        LEFT OUTER JOIN
        ref_source_country_code_mapping          m_code
           ON  m_code.source_country_code        = NULLIF(UPPER(TRIM(t.country_code)), '')
        LEFT OUTER JOIN
        ref_country                              r
          ON  r.country_code                    = COALESCE(NULLIF(m_name.country_code, ''), NULLIF(m_code.country_code, ''), 'GB')
  WHERE NULLIF(TRIM(t.payment_terms_id), '')    IS NOT NULL
;
