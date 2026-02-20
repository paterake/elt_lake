-- ============================================================================
-- VALIDATE: Supplier Alternate Name
-- Source table: workday_supplier_alternate_name
-- Note: This table is currently always empty (WHERE 1=2 in transform SQL).
--       Rules are recorded here for completeness and to guard future changes.
-- VBA rules: Missing (Supplier ID), Match (cross-tab), Match (usage type)
-- ============================================================================
CREATE TABLE IF NOT EXISTS validation_supplier_issues (
    sheet       VARCHAR
  , rule_type   VARCHAR
  , col         VARCHAR
  , supplier_id VARCHAR
  , detail      VARCHAR
  , message     VARCHAR
)
;

-- ----------------------------------------------------------------------------
-- MISSING: Supplier ID is required on every row
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Alternate Name'                          sheet
     , 'MISSING'                                         rule_type
     , 'supplier_id'                                     col
     , a.supplier_id                                     supplier_id
     , NULL                                              detail
     , 'Supplier ID is a required column.'               message
  FROM workday_supplier_alternate_name                   a
 WHERE a.supplier_id IS NULL
    OR TRIM(a.supplier_id) = ''
;

-- ----------------------------------------------------------------------------
-- CROSS_TAB: Supplier ID must exist in Supplier Name tab
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Alternate Name'                                         sheet
     , 'CROSS_TAB'                                                      rule_type
     , 'supplier_id'                                                    col
     , a.supplier_id                                                    supplier_id
     , a.supplier_id                                                    detail
     , 'Supplier ID must be listed first on the Supplier Name tab.'     message
  FROM workday_supplier_alternate_name                                  a
  LEFT OUTER JOIN
       workday_supplier_name                                            n
         ON  n.supplier_id                                              = a.supplier_id
 WHERE n.supplier_id IS NULL
   AND a.supplier_id IS NOT NULL
;

-- ----------------------------------------------------------------------------
-- MATCH: Alternate Name Usage must be a valid value
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Alternate Name'                                           sheet
     , 'MATCH'                                                            rule_type
     , 'alternate_name_usage_plus'                                        col
     , a.supplier_id                                                      supplier_id
     , a.alternate_name_usage_plus                                        detail
     , 'The alternate name usage must match the drop-down values: "Short Name", "Check Name".' message
  FROM workday_supplier_alternate_name                                    a
 WHERE a.alternate_name_usage_plus IS NOT NULL
   AND a.alternate_name_usage_plus NOT IN ('Short Name', 'Check Name')
;
