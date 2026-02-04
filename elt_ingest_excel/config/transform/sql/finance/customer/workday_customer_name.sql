DROP TABLE IF EXISTS workday_customer_name
;
CREATE TABLE workday_customer_name
    AS
SELECT
       c.customer_id                                              customer_id
     , c.customer_id_name                                         customer_name
     , TRIM(c.customer_number)                                    reference_id
     , UPPER(TRIM(c.customer_class))                              customer_category
     , UPPER(TRIM(c.company))                                     business_entity_name
     , TRIM(c.customer_number)                                    external_entity_id
     , COALESCE(NULLIF(UPPER(TRIM(c.country_code)), ''), 'GB')    preferred_locale
     , COALESCE(m.language_code, 'EN')                            preferred_language
     , NULL                                                       lockbox
     , UPPER(TRIM(c.company))                                     customer_security_segment
     , NULL                                                       worktag_only
     , CASE
         WHEN UPPER(TRIM(c.inactive)) = 'NO'
         THEN 'Yes'
         ELSE 'No'
       END                                                        submit
     , NULL                                                       create_customer_from_financial_institution
     , NULL                                                       create_customer_from_supplier
     , NULL                                                       create_customer_from_tax_authority
     , NULL                                                       create_customer_from_investor
  FROM src_fin_customer                c
       LEFT OUTER JOIN
       ref_customer_country_language   m
          ON m.country_code            = COALESCE(NULLIF(UPPER(TRIM(c.country_code)), ''), 'GB')
;
