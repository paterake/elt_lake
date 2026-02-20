-- ============================================================================
-- VALIDATE: Supplier Company Restrictions
-- Source table: workday_supplier_company_restrictions
-- VBA rules: Match (cross-tab Supplier ID), Missing (restricted_to_companies)
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
       'Supplier Company Restrictions'                                  sheet
     , 'CROSS_TAB'                                                     rule_type
     , 'supplier_id'                                                   col
     , r.supplier_id                                                   supplier_id
     , r.supplier_id                                                   detail
     , 'Supplier ID must be listed first on the Supplier Name tab.'    message
  FROM workday_supplier_company_restrictions                           r
  LEFT OUTER JOIN
       workday_supplier_name                                           n
         ON  n.supplier_id                                             = r.supplier_id
 WHERE n.supplier_id IS NULL
;

-- ----------------------------------------------------------------------------
-- MISSING: Restricted To Companies must be populated
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Company Restrictions'                                  sheet
     , 'MISSING'                                                       rule_type
     , 'restricted_to_companies'                                       col
     , r.supplier_id                                                   supplier_id
     , NULL                                                            detail
     , 'Restricted To Companies must be populated for every row.'      message
  FROM workday_supplier_company_restrictions                           r
 WHERE r.restricted_to_companies IS NULL
    OR TRIM(r.restricted_to_companies) = ''
;

-- ----------------------------------------------------------------------------
-- MISSING: Every supplier in Supplier Name must have a Company Restrictions row
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Company Restrictions'                                      sheet
     , 'MISSING'                                                           rule_type
     , 'restricted_to_companies'                                           col
     , n.supplier_id                                                       supplier_id
     , NULL                                                                detail
     , 'Supplier has no row in Supplier Company Restrictions tab.'         message
  FROM workday_supplier_name                                               n
  LEFT OUTER JOIN
       workday_supplier_company_restrictions                               r
         ON  r.supplier_id                                                 = n.supplier_id
 WHERE r.supplier_id IS NULL
;
