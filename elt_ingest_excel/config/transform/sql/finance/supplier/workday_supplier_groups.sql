DROP TABLE IF EXISTS workday_supplier_groups
;
CREATE TABLE workday_supplier_groups 
    AS
SELECT
       TRIM(supplier_id)                           supplier_id
     , TRIM(vendor_name)                           supplier_name
     , 'GROUP1'                                    supplier_group
  FROM src_fin_supplier
 WHERE vendor_class_id IS NOT NULL
   AND TRIM(vendor_class_id) != ''
;
