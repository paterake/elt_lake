DROP TABLE IF EXISTS workday_supplier_groups
;
CREATE TABLE workday_supplier_groups 
    AS
SELECT
       s.supplier_id                                  supplier_id
     , s.nrm_vendor_name                              supplier_name
     , CASE
           WHEN UPPER(SUBSTR(s.nrm_vendor_name, 1, 1)) BETWEEN 'A' AND 'L'
               THEN 'Suppliers_A_L'
           WHEN UPPER(SUBSTR(s.nrm_vendor_name, 1, 1)) BETWEEN 'M' AND 'Z'
               THEN 'Suppliers_M_Z'
           ELSE 'Suppliers_0_9'
       END                                            supplier_group
  FROM src_fin_supplier s
;
