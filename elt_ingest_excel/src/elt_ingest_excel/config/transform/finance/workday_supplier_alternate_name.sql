DROP TABLE IF EXISTS workday_supplier_alternate_name
;
CREATE TABLE workday_supplier_alternate_name AS
-- Short Name
SELECT
       TRIM(vendor_id)                             supplier_id
     , TRIM(vendor_name)                           supplier_name
     , TRIM(vendor_short_name)                     alternate_name
     , 'Short_Name'                                alternate_name_usage_plus
  FROM src_fin_supplier
 WHERE vendor_short_name IS NOT NULL
   AND TRIM(vendor_short_name) != ''
   AND TRIM(vendor_short_name) != TRIM(vendor_name)

UNION ALL

-- Check/Payment Name
SELECT
       TRIM(vendor_id)                             supplier_id
     , TRIM(vendor_name)                           supplier_name
     , TRIM(vendor_check_name)                     alternate_name
     , 'Payment_Name'                              alternate_name_usage_plus
  FROM src_fin_supplier
 WHERE vendor_check_name IS NOT NULL
   AND TRIM(vendor_check_name) != ''
   AND TRIM(vendor_check_name) != TRIM(vendor_name)
   AND (TRIM(vendor_check_name) != TRIM(vendor_short_name)
        OR vendor_short_name IS NULL)
;
