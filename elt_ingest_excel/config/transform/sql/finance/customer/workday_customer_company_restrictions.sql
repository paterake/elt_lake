DROP TABLE IF EXISTS workday_customer_company_restrictions
;
CREATE TABLE workday_customer_company_restrictions
    AS
SELECT
       c.customer_id                                     customer_id
     , c.nrm_customer_name                               customer_name
     , COALESCE(m.target_value, TRIM(bu.business_unit))  restricted_to_companies
  FROM 
       src_fin_customer                                  c
       CROSS JOIN LATERAL
       UNNEST(c.array_business_unit)                     bu(business_unit)
       LEFT OUTER JOIN
       ref_source_business_unit_mapping                  m
         ON  m.source_value                              = UPPER(TRIM(bu.business_unit))
;
