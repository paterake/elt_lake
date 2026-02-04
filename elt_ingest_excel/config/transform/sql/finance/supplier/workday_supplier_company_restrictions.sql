DROP TABLE IF EXISTS workday_supplier_company_restrictions
;
CREATE TABLE workday_supplier_company_restrictions 
    AS
SELECT
       s.supplier_id                                  supplier_id
     , s.nrm_vendor_name                             supplier_name
     , CASE TRIM(s.company)
         WHEN 'FA' THEN 'The Football Association'
         ELSE TRIM(s.company)
       END                                         restricted_to_companies
  FROM src_fin_supplier s
 WHERE s.company IS NOT NULL
   AND TRIM(s.company) != ''
;
