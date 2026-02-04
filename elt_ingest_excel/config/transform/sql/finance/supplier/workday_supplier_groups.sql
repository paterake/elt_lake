DROP TABLE IF EXISTS workday_supplier_groups
;
CREATE TABLE workday_supplier_groups 
    AS
SELECT
       TRIM(s.supplier_id)                           supplier_id
     , TRIM(s.vendor_name)                           supplier_name
     , CASE
           WHEN UPPER(SUBSTR(TRIM(s.vendor_name), 1, 1)) BETWEEN 'A' AND 'L'
               THEN 'Suppliers_A_L'
           WHEN UPPER(SUBSTR(TRIM(s.vendor_name), 1, 1)) BETWEEN 'M' AND 'Z'
               THEN 'Suppliers_M_Z'
           ELSE 'Suppliers_0_9'
       END                                           supplier_group
  FROM src_fin_supplier s
 WHERE s.vendor_class_id IS NOT NULL
   AND TRIM(s.vendor_class_id) != ''
;
