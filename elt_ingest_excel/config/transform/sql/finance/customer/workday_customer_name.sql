DROP TABLE IF EXISTS workday_customer_name
;
CREATE TABLE workday_customer_name
    AS
SELECT
       t.customer_id                   customer_id
     , t.nrm_customer_name             customer_name
     , t.nrm_agg_customer_number       reference_id
     , r.target_value                  customer_category
     , NULL                            business_entity_name
     , NULL                            external_entity_id
     , NULL                            preferred_locale
     , NULL                            preferred_language
     , NULL                            lockbox
     , NULL                            customer_security_segment
     , NULL                            worktag_only
     , NULL                            submit
     , NULL                            create_customer_from_financial_institution
     , NULL                            create_customer_from_supplier
     , NULL                            create_customer_from_tax_authority
     , NULL                            create_customer_from_investor
  FROM src_fin_customer                t
       LEFT OUTER JOIN
       ref_customer_class              r
          ON UPPER(TRIM(r.source_value)) = COALESCE(NULLIF(UPPER(TRIM(t.customer_class)), ''), 'DEFAULT')
;
