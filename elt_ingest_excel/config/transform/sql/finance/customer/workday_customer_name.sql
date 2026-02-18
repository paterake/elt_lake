DROP TABLE IF EXISTS workday_customer_name
;
CREATE TABLE workday_customer_name
    AS
SELECT
       c.customer_id                                                             customer_id
     , c.nrm_customer_name                                                       customer_name
     , c.nrm_customer_number                                                     reference_id
     , COALESCE(NULLIF(UPPER(TRIM(c.customer_class)), ''), 'Customer Category')  customer_category
     , NULL                                                                      business_entity_name
     , c.nrm_customer_number                                                     external_entity_id
     , c.nrm_country_code                                                        preferred_locale
     , c.nrm_language_code                                                       preferred_language
     , NULL                                                                      lockbox
     , NULL                                                                      customer_security_segment
     , NULL                                                                      worktag_only
     , CASE
         WHEN UPPER(TRIM(c.inactive)) = 'NO'
         THEN 'Yes'
         ELSE 'No'
       END                                                                       submit
     , NULL                                                                      create_customer_from_financial_institution
     , NULL                                                                      create_customer_from_supplier
     , NULL                                                                      create_customer_from_tax_authority
     , NULL                                                                      create_customer_from_investor
  FROM src_fin_customer                c
;
