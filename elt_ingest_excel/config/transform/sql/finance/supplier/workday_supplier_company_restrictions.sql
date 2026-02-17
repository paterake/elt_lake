DROP TABLE IF EXISTS workday_supplier_company_restrictions
;
CREATE TABLE workday_supplier_company_restrictions
    AS
SELECT
        s.supplier_id                                  supplier_id
      , s.nrm_vendor_name                              supplier_name
      , CASE TRIM(bu.business_unit)
          WHEN 'FA' THEN 'The Football Association'
          ELSE TRIM(bu.business_unit)
        END                                            restricted_to_companies
  FROM src_fin_supplier                                s
       CROSS JOIN LATERAL
       UNNEST(s.business_units)                        bu(business_unit)
;
