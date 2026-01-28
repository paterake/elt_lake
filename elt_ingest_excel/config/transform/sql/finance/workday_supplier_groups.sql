DROP TABLE IF EXISTS workday_supplier_groups
;
CREATE TABLE workday_supplier_groups 
    AS
SELECT
       TRIM(supplier_id)                           supplier_id
     , TRIM(vendor_name)                           supplier_name
     , CASE
         WHEN TRIM(vendor_class_id) = 'GENERAL'    THEN 'General Suppliers'
         WHEN TRIM(vendor_class_id) = 'CONSULTING' THEN 'Professional Services'
         WHEN TRIM(vendor_class_id) = 'IT'         THEN 'Technology Suppliers'
         WHEN TRIM(vendor_class_id) = 'FACILITIES' THEN 'Facilities & Maintenance'
         WHEN TRIM(vendor_class_id) = 'MARKETING'  THEN 'Marketing Services'
         ELSE TRIM(vendor_class_id)
       END                                         supplier_group
  FROM src_fin_supplier
 WHERE vendor_class_id IS NOT NULL
   AND TRIM(vendor_class_id) != ''
;
