DROP TABLE IF EXISTS ref_supplier_category_mapping
;
-- Maps dirty source supplier categories (from vendor_class_id)
-- to canonical Workday supplier categories (valid values)
-- Valid targets:
-- - Information Technology
-- - Office Supplies
-- - Professional Services
-- - Property Managers
-- - Services
-- - Utilities
CREATE TABLE ref_supplier_category_mapping
    AS
SELECT
       TRIM(source_supplier_category)      source_supplier_category
     , TRIM(supplier_category)             supplier_category
  FROM read_json_auto(
           '/Users/rpatel/Documents/__code/git/emailrak/elt_lake/elt_ingest_excel/config/data/ref_supplier_category_mapping.json'
       )
;
