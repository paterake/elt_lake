DROP TABLE IF EXISTS workday_supplier_alternate_name
;
CREATE TABLE workday_supplier_alternate_name
    AS
  WITH cte_supplier_alternate_name
    AS (
-- Short Name
SELECT
       s.supplier_id                                  supplier_id
     , s.nrm_vendor_name                              supplier_name
     , TRIM(s.vendor_short_name)                      alternate_name
     , 'Short Name'                                   alternate_name_usage_plus
  FROM src_fin_supplier s
 WHERE s.vendor_short_name             IS NOT NULL
   AND TRIM(s.vendor_short_name)       != ''
   AND TRIM(s.vendor_short_name)       != s.nrm_vendor_name
UNION ALL
-- Check Name
SELECT
       s.supplier_id                                  supplier_id
     , s.nrm_vendor_name                              supplier_name
     , TRIM(s.vendor_check_name)                      alternate_name
     , 'Check Name'                                   alternate_name_usage_plus
  FROM src_fin_supplier s
 WHERE s.vendor_check_name             IS NOT NULL
   AND TRIM(s.vendor_check_name)       != ''
   AND TRIM(s.vendor_check_name)       != s.nrm_vendor_name
   AND (
       TRIM(s.vendor_check_name)       != TRIM(s.vendor_short_name)
    OR s.vendor_short_name             IS NULL
       )
       )
SELECT *
  FROM cte_supplier_alternate_name
 WHERE 1 = 2
;



Vendor Name                            Vendor Short Name   Vendor Check Name
CHARNOCK RIDGEWAY WOMEN AND GIRLS FC  CHARNOCK RIDGEW   CHARNOCK RIDGEWAY WOMEN AND GIRLS FC  