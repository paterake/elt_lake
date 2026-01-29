DROP TABLE IF EXISTS workday_customer_company_restrictions
;
CREATE TABLE workday_customer_company_restrictions
    AS
SELECT
       TRIM(customer_id)                             customer_id
     , TRIM(customer_name)                           customer_name
     , CASE TRIM(company)
         WHEN 'FA' THEN 'The Football Association'
         ELSE TRIM(company)
       END                                           restricted_to_companies
  FROM src_fin_customer
 WHERE company IS NOT NULL
   AND TRIM(company) != ''
;
