DROP TABLE IF EXISTS workday_supplier_company_restrictions
;
CREATE TABLE workday_supplier_company_restrictions
    AS
SELECT
        s.supplier_id                                    supplier_id
      , s.nrm_vendor_name                                supplier_name
      , COALESCE(m.target_value, TRIM(bu.business_unit)) restricted_to_companies
  FROM 
       src_fin_supplier                                  s
       CROSS JOIN LATERAL
       UNNEST(s.business_units)                          bu(business_unit)
       LEFT OUTER JOIN
       ref_source_business_unit_mapping                  m
         ON  m.source_value                              = UPPER(TRIM(bu.business_unit))
;
