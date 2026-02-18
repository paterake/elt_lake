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
;

todo: collapse to a single row per supplier.
