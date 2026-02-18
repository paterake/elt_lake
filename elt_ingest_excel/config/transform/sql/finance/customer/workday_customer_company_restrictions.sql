DROP TABLE IF EXISTS workday_customer_company_restrictions
;
CREATE TABLE workday_customer_company_restrictions
    AS
SELECT
       c.customer_id                                  customer_id
     , c.nrm_customer_name                            customer_name
     , CASE TRIM(c.company)
         WHEN 'FA' THEN 'The Football Association'
         ELSE TRIM(c.company)
       END                                            restricted_to_companies
  FROM src_fin_customer                c
 WHERE c.company IS NOT NULL
   AND TRIM(c.company) != ''
;
