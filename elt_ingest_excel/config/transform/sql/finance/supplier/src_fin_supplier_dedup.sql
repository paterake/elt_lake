INSTALL splink_udfs FROM community;
LOAD splink_udfs;

DROP TABLE IF EXISTS src_fin_supplier;

CREATE TABLE src_fin_supplier AS
WITH raw_data AS (
    SELECT t.*
         , UPPER(TRIM(t.nrm_vendor_name)) as orig_name
         -- Normalize Name: Remove common suffixes and special chars for comparison
         , UPPER(REGEXP_REPLACE(REGEXP_REPLACE(t.nrm_vendor_name, '[^a-zA-Z0-9\s]', '', 'g'), '\b(LTD|LIMITED|PLC|FC|AFC|WOMEN|WOMENS|LFC)\b', '', 'gi')) as clean_name
         -- Normalize Postcode: Remove spaces
         , UPPER(REGEXP_REPLACE(t.post_code, '\s+', '', 'g')) as clean_postcode
         -- Bank Details
         , NULLIF(TRIM(t.eft_bank_code), '') as sort_code
         , NULLIF(TRIM(t.eft_bank_account), '') as account_number
    FROM src_fin_supplier_raw t
    WHERE t.data_rnk = 1
),
grouped_keys AS (
    SELECT t.*
         , COALESCE(
             -- Rule: Soundex Name Match AND Same Bank Details (Strict Deduplication)
             CASE WHEN sort_code IS NOT NULL 
                   AND account_number IS NOT NULL
                   AND clean_name IS NOT NULL 
                   AND LENGTH(clean_name) > 2
                  THEN 'MERGE:' || SOUNDEX(clean_name) || ':' || sort_code || ':' || account_number
             END,
             -- Fallback: Treat as unique
             'ORIG:' || t.vendor_id
           ) as dedup_key
    FROM raw_data t
),
-- Rank records within each group to pick the "Survivor" (Main Record)
-- Preference: Most recent activity, then most complete data
ranked_groups AS (
    SELECT t.*
         , ROW_NUMBER() OVER (
             PARTITION BY dedup_key 
             ORDER BY 
                COALESCE(last_purchase_ts, created_ts, '1900-01-01') DESC,
                vendor_id DESC
           ) as group_rnk
    FROM grouped_keys t
),
-- Aggregate Contact Details for the group
aggregated_contacts AS (
    SELECT dedup_key
         , STRING_AGG(DISTINCT NULLIF(TRIM(email_to_address), ''), '; ') as combined_emails
         , STRING_AGG(DISTINCT NULLIF(TRIM(phone_number_1), ''), '; ') as combined_phones
    FROM grouped_keys
    GROUP BY dedup_key
),
final_deduped AS (
    SELECT m.*
         , a.combined_emails
         , a.combined_phones
    FROM ranked_groups m
    JOIN aggregated_contacts a ON m.dedup_key = a.dedup_key
    WHERE m.group_rnk = 1
),
cte_supplier_rnk AS (
    SELECT t.*
         , ROW_NUMBER() OVER(ORDER BY t.nrm_vendor_name) as rnk
    FROM final_deduped t
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
      , NULLIF(TRIM(t.sort_code), '')                                                  nrm_bank_sort_code
      , rbsc.bank_name_primary                                                         nrm_bank_name
      , t.vendor_id                                                                    nrm_vendor_id
      , t.vendor_id_count
      , t.vendor_id_rnk
      , t.data_rnk
      , t.key_count
      , t.vendor_id
      , t.nrm_vendor_name
      , t.key_vendor_name
      , t.created_ts
      , t.last_payment_ts
      , t.last_purchase_ts
      , t.business_unit
      , t.company
      , t.vendor_id_1
      , t.vendor_name
      , t.vendor_short_name
      , t.vendor_check_name
      , t.vendor_class_id
      , t.vendor_status
      , t.vendor_address_code_primary
      , t.address_1
      , t.address_2
      , t.address_3
      , t.city
      , t.county
      , t.post_code
      , t.country_code
      , t.country
      , t.vendor_contact
      , t.vendor_address_code_purchase_address
      , t.vendor_address_code_remit_to
      , t.vendor_address_code_ship_from
      , t.hold
      , t.combined_phones                                                              phone_number_1
      , t.phone_number_2
      , t.phone_3
      , t.fax_number
      , t.tax_schedule_id
      , t.shipping_method
      , t.creditor_account
      , t.comment1
      , t.comment2
      , t.currency_id
      , t.rate_type_id
      , t.payment_terms_id
      , t.discount_grace_period
      , t.due_date_grace_period
      , t.payment_priority
      , t.minimum_order
      , t.trade_discount
      , t.tax_id_number
      , t.tax_registration_number
      , t.checkbook_id
      , t.old_creditor
      , t.user_defined_2
      , t.minimum_payment_type
      , t.maximum_invoice_amount_for_vendors
      , t.credit_limit
      , t.writeoff
      , t.revalue_vendor
      , t.post_results_to
      , t.created_date
      , t.last_purchase_date
      , t.last_payment_date
      , t.current_balance
      , t.master_type
      , t.combined_emails                                                              email_to_address
      , t.email_cc_address
      , t.email_bcc_address
      , t.series
      , t.customer_vendor_id
      , t.eft_address_code
      , t.eft_vendor_id
      , t.customer_id
      , t.eft_bank_type
      , t.additional_information
      , t.inactive
      , t.bank_name
      , t.eft_bank_account
      , t.eft_bank_account_verify
      , t.eft_bank_branch
      , t.giro_post_type
      , t.eft_bank_code
      , t.eft_bank_code_verify
      , t.eft_bank_branch_code
      , t.eft_bank_check_digit
      , t.building_society_roll_no
      , t.iban
      , t.swift_address
      , t.swift_address_verify
      , t.customer_vendor_country_code
      , t.delivery_country_code
      , t.bank_country_code
      , t.central_bank_code
      , t.addressline_1
      , t.addressline_2
      , t.addressline_3
      , t.addressline_4
      , t.regulatorycode_1
      , t.regulatorycode_2
      , t.bankinfo7
      , t.eft_transit_routing_no
      , t.currencyid
      , t.e_banking_payment
      , t.bank_account_number
      , t.payment_file_name
      , t.payment_file_date
      , t.source_entity_name
      , t.source_entity_id
      , t.source_entity_source
      , t.source_entity_type
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
          ON rbsc.sort_code_prefix              = SUBSTR(NULLIF(TRIM(t.sort_code), ''), 1, 2)
  WHERE NULLIF(TRIM(t.payment_terms_id), '')    IS NOT NULL
;
