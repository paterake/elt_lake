
INSTALL splink_udfs FROM community;
LOAD splink_udfs;

DROP TABLE IF EXISTS src_fin_customer;

CREATE TABLE src_fin_customer AS
WITH raw_data AS (
    SELECT t.*
         , UPPER(TRIM(t.nrm_customer_name)) as orig_name
         , UPPER(REGEXP_REPLACE(t.post_code, '\s+', '', 'g')) as clean_postcode
         -- Clean Name: Remove generic suffixes
         , UPPER(REGEXP_REPLACE(REGEXP_REPLACE(t.nrm_customer_name, '[^a-zA-Z0-9\s]', '', 'g'), '\y(LTD|LIMITED|PLC|GROUP|HOLDINGS)\y', '', 'gi')) as clean_name
         -- Check for distinct entities to keep separate
         , CASE WHEN t.nrm_customer_name ~* '\y(WOMEN|WOMENS|LADIES|FOUNDATION|TRUST|COMMUNITY)\y' THEN 1 ELSE 0 END as is_distinct_entity
    FROM src_fin_customer_raw t
    WHERE t.data_rnk = 1
),
grouped_keys AS (
    SELECT t.*
         , COALESCE(
             -- Rule 1: Special Entities (Women/Foundation/Trust) -> Keep Separate
             CASE WHEN is_distinct_entity = 1 
                  THEN 'DISTINCT:' || TRIM(orig_name) || ':' || clean_postcode
             END,
             -- Rule 2: Similar Name (Soundex) + Same Postcode -> Merge
             CASE WHEN clean_name IS NOT NULL AND LENGTH(clean_name) > 2 AND clean_postcode IS NOT NULL AND LENGTH(clean_postcode) > 4
                  THEN 'MERGE:' || SOUNDEX(clean_name) || ':' || clean_postcode
             END,
             -- Fallback: Treat as unique
             'ORIG:' || t.customer_id
           ) as dedup_key
    FROM raw_data t
),
ranked_groups AS (
    SELECT t.*
         , ROW_NUMBER() OVER (
             PARTITION BY dedup_key 
             ORDER BY 
                COALESCE(last_transaction_ts, created_ts, '1900-01-01') DESC,
                customer_id DESC
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
      , t.customer_id                                                                  nrm_customer_number
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
