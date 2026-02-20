-- ============================================================================
-- VALIDATE: Supplier Groups
-- Source table: workday_supplier_groups
-- VBA rules: Match (cross-tab Supplier ID), Match (group name), CheckDuplicateCombinationColumns
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
-- CROSS_TAB: Supplier ID must exist in Supplier Name tab
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Groups'                                               sheet
     , 'CROSS_TAB'                                                    rule_type
     , 'supplier_id'                                                  col
     , g.supplier_id                                                  supplier_id
     , g.supplier_id                                                  detail
     , 'Supplier ID must be listed first on the Supplier Name tab.'   message
  FROM workday_supplier_groups                                        g
  LEFT OUTER JOIN
       workday_supplier_name                                          n
         ON  n.supplier_id                                            = g.supplier_id
 WHERE n.supplier_id IS NULL
;

-- ----------------------------------------------------------------------------
-- MATCH: Supplier Group must be a valid named-range value
-- Note: workday_supplier_groups.sql generates 'Suppliers_A_L' (underscores)
--       but the workbook named range expects 'Suppliers A-L' (space/hyphen).
--       Rows flagged here indicate a mismatch with the Excel drop-down list.
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Groups'                                                   sheet
     , 'MATCH'                                                            rule_type
     , 'supplier_group'                                                   col
     , g.supplier_id                                                      supplier_id
     , g.supplier_group                                                   detail
     , 'The Supplier Group name must match the drop-down values: "Suppliers 0-9", "Suppliers A-L", "Suppliers M-Z".' message
  FROM workday_supplier_groups                                            g
 WHERE g.supplier_group NOT IN
       (
         'Suppliers 0-9'
       , 'Suppliers A-L'
       , 'Suppliers M-Z'
       )
;

-- ----------------------------------------------------------------------------
-- DUPLICATE_COMBO: Supplier ID + Supplier Group combination must be unique
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Groups'                                                     sheet
     , 'DUPLICATE_COMBO'                                                    rule_type
     , 'supplier_id + supplier_group'                                       col
     , g.supplier_id                                                        supplier_id
     , g.supplier_group                                                     detail
     , 'The Supplier Group must be unique for each Supplier ID.'            message
  FROM workday_supplier_groups                                              g
 WHERE (g.supplier_id, g.supplier_group) IN
       (
         SELECT d.supplier_id, d.supplier_group
           FROM workday_supplier_groups                                      d
          GROUP BY d.supplier_id, d.supplier_group
         HAVING COUNT(*) > 1
       )
;
