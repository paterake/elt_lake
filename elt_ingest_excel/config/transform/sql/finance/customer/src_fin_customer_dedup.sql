
INSTALL splink_udfs FROM community;
LOAD splink_udfs;

DROP TABLE IF EXISTS src_fin_customer_dedup;

CREATE TABLE src_fin_customer_dedup AS
WITH scored_data AS (
    SELECT t.*
         , UPPER(TRIM(t.nrm_customer_name)) as orig_name
         , UPPER(REGEXP_REPLACE(t.nrm_postal_code, '\s+', '', 'g')) as clean_postcode
         -- Clean Name: Remove generic suffixes (even if joined, e.g. BOOKINGSLTD) and periods
         , UPPER(REGEXP_REPLACE(REGEXP_REPLACE(REPLACE(t.nrm_customer_name, '.', ''), '[^a-zA-Z0-9\s]', '', 'g'), '(\s|\b)(LTD|LIMITED|PLC|GROUP|HOLDINGS|FC|FOOTBALL|CLUB|ASSOCIATION)\b', '', 'gi')) as clean_name
         -- Categorize Entity Type
         , CASE 
             WHEN REGEXP_MATCHES(t.nrm_customer_name, '\b(WOMEN|WOMENS|LADIES)\b', 'i') THEN 'WOMEN'
             WHEN REGEXP_MATCHES(t.nrm_customer_name, '\b(FOUNDATION|TRUST|COMMUNITY)\b', 'i') THEN 'FOUNDATION'
             ELSE 'MAIN'
           END as entity_type
         -- Calculate Completeness Score (Using Normalized Fields from src_fin_customer)
         , (
             (CASE WHEN NULLIF(TRIM(t.payment_terms_id), '') IS NOT NULL THEN 50 ELSE 0 END) +
             (CASE WHEN NULLIF(TRIM(t.tax_schedule_id), '') IS NOT NULL THEN 40 ELSE 0 END) +
             (CASE WHEN NULLIF(TRIM(t.tax_registration_number), '') IS NOT NULL THEN 30 ELSE 0 END) +
             (CASE WHEN t.nrm_address_line_1 IS NOT NULL THEN 20 ELSE 0 END) +
             (CASE WHEN t.nrm_address_line_2 IS NOT NULL THEN 10 ELSE 0 END) +
             (CASE WHEN t.nrm_address_line_3 IS NOT NULL THEN 5 ELSE 0 END) +
             (CASE WHEN t.nrm_postal_code IS NOT NULL THEN 20 ELSE 0 END) +
             (CASE WHEN t.nrm_city IS NOT NULL THEN 10 ELSE 0 END) +
             (CASE WHEN t.nrm_region IS NOT NULL THEN 10 ELSE 0 END)
           ) as completeness_score
    FROM src_fin_customer t
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
         , STRING_AGG(DISTINCT NULLIF(TRIM(nrm_customer_number), ''), '|') as combined_nrm_customer_number
         , STRING_AGG(DISTINCT NULLIF(TRIM(phone_1), ''), '; ')             as combined_phone_1
         , STRING_AGG(DISTINCT NULLIF(TRIM(phone_2), ''), '; ')             as combined_phone_2
         , STRING_AGG(DISTINCT NULLIF(TRIM(phone_3), ''), '; ')             as combined_phone_3
         , STRING_AGG(DISTINCT NULLIF(TRIM(fax), ''), '; ')                 as combined_fax
         , STRING_AGG(DISTINCT NULLIF(TRIM(email_to_address) , ''), ';')    as combined_email_to_address
         , STRING_AGG(DISTINCT NULLIF(TRIM(email_cc_address) , ''), ';')    as combined_email_cc_address
         , STRING_AGG(DISTINCT NULLIF(TRIM(email_bcc_address), ''), '; ')   as combined_email_bcc_address
    FROM grouped_keys
    GROUP BY dedup_key
),
final_deduped AS (
    SELECT m.*
         , a.combined_nrm_customer_number
         , a.combined_phone_1
         , a.combined_phone_2
         , a.combined_phone_3
         , a.combined_fax
         , a.combined_email_to_address
         , a.combined_email_cc_address
         , a.combined_email_bcc_address
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
      , t.* EXCLUDE (
            customer_id
          , nrm_customer_number
          , phone_1
          , phone_2
          , phone_3
          , fax
          , email_to_address
          , email_cc_address
          , email_bcc_address
        )
      , t.combined_nrm_customer_number                                                 nrm_customer_number
      , t.combined_phone_1                                                             phone_1
      , t.combined_phone_2                                                             phone_2
      , t.combined_phone_3                                                             phone_3
      , t.combined_fax                                                                 fax
      , t.combined_email_to_address                                                    email_to_address
      , t.combined_email_cc_address                                                    email_cc_address
      , t.combined_email_bcc_address                                                   email_bcc_address
   FROM cte_customer_rnk                         t
  WHERE NULLIF(TRIM(t.payment_terms_id), '')    IS NOT NULL
;
