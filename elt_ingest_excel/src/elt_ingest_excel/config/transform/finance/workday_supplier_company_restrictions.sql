DROP TABLE IF EXISTS workday_supplier_company_restrictions
;
CREATE TABLE workday_supplier_company_restrictions AS
SELECT
       TRIM(vendor_id)                             supplier_id
     , TRIM(vendor_name)                           supplier_name
     , CASE TRIM(company)
         WHEN 'FA' THEN 'The Football Association'
         ELSE TRIM(company)
       END                                         restricted_to_companies
  FROM src_fin_supplier
 WHERE company IS NOT NULL
   AND TRIM(company) != ''
;
