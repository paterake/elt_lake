DROP TABLE IF EXISTS workday_customer_name
;
CREATE TABLE workday_customer_name
    AS
SELECT
       TRIM(customer_id)                             customer_id
     , TRIM(customer_name)                           customer_name
     , TRIM(customer_number)                         reference_id
     , CASE
         WHEN TRIM(customer_class) = 'OTHER'         THEN 'Other Customers'
         ELSE 'Customers'
       END                                           customer_category
     , TRIM(customer_name)                           business_entity_name
     , TRIM(customer_number)                         external_entity_id
     , NULL                                          preferred_locale
     , NULL                                          preferred_language
     , NULL                                          lockbox
     , NULL                                          customer_security_segment
     , NULL                                          worktag_only
     , CASE
         WHEN UPPER(TRIM(inactive)) = 'NO'           THEN 'Yes'
         ELSE 'No'
       END                                           submit
     , NULL                                          create_customer_from_financial_institution
     , NULL                                          create_customer_from_supplier
     , NULL                                          create_customer_from_tax_authority
     , NULL                                          create_customer_from_investor
  FROM src_fin_customer
;
