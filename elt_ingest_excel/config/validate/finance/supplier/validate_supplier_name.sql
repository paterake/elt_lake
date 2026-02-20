-- ============================================================================
-- VALIDATE: Supplier Name
-- Source table: workday_supplier_name
-- VBA rules: Duplicatecolumn, Missing, Match, EnsureDataMultipleColumns
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
-- DUPLICATE: Supplier ID must be unique
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Name'                                           sheet
     , 'DUPLICATE'                                              rule_type
     , 'supplier_id'                                            col
     , n.supplier_id                                            supplier_id
     , n.supplier_id                                            detail
     , 'Supplier ID must be unique and cannot be duplicated.'   message
  FROM workday_supplier_name                                    n
 WHERE n.supplier_id IN
       (
         SELECT d.supplier_id
           FROM workday_supplier_name                           d
          GROUP BY d.supplier_id
         HAVING COUNT(*) > 1
       )
;

-- ----------------------------------------------------------------------------
-- DUPLICATE: Supplier Name must be unique
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Name'                                           sheet
     , 'DUPLICATE'                                              rule_type
     , 'supplier_name'                                          col
     , n.supplier_id                                            supplier_id
     , n.supplier_name                                          detail
     , 'Supplier Name must be unique and cannot be duplicated.' message
  FROM workday_supplier_name                                    n
 WHERE n.supplier_name IN
       (
         SELECT d.supplier_name
           FROM workday_supplier_name                           d
          GROUP BY d.supplier_name
         HAVING COUNT(*) > 1
       )
;

-- ----------------------------------------------------------------------------
-- DUPLICATE: Reference ID must be unique
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Name'                                           sheet
     , 'DUPLICATE'                                              rule_type
     , 'reference_id'                                           col
     , n.supplier_id                                            supplier_id
     , n.reference_id                                           detail
     , 'Reference ID must be unique and cannot be duplicated.'  message
  FROM workday_supplier_name                                    n
 WHERE n.reference_id IS NOT NULL
   AND n.reference_id IN
       (
         SELECT d.reference_id
           FROM workday_supplier_name                           d
          WHERE d.reference_id IS NOT NULL
          GROUP BY d.reference_id
         HAVING COUNT(*) > 1
       )
;

-- ----------------------------------------------------------------------------
-- MISSING: Supplier Category is required
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Name'                                                   sheet
     , 'MISSING'                                                         rule_type
     , 'supplier_category'                                               col
     , n.supplier_id                                                     supplier_id
     , NULL                                                              detail
     , 'Supplier Category is a required column and must be populated.'   message
  FROM workday_supplier_name                                             n
 WHERE n.supplier_category IS NULL
    OR TRIM(n.supplier_category) = ''
;

-- ----------------------------------------------------------------------------
-- MATCH: Supplier Category must be a valid value
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Name'                                                    sheet
     , 'MATCH'                                                           rule_type
     , 'supplier_category'                                               col
     , n.supplier_id                                                     supplier_id
     , n.supplier_category                                               detail
     , 'Please select a supplier category from the drop-down list.'      message
  FROM workday_supplier_name                                             n
 WHERE n.supplier_category IS NOT NULL
   AND TRIM(n.supplier_category) != ''
   AND n.supplier_category NOT IN
       (
         'Benefits'
       , 'Consulting Services and Professional Fees'
       , 'Facilities'
       , 'Information Technology'
       , 'Legal'
       , 'Medical Supplies'
       , 'Office Supplies'
       , 'Other'
       , 'Utilities'
       , 'Travel and Accomodation'
       , 'Referees'
       , 'Panel Members'
       , 'Football Clubs'
       , 'Barclays Girls Football School Partnerships'
       , 'Marketing'
       , 'Education'
       , 'Catering'
       )
;

-- ----------------------------------------------------------------------------
-- MATCH: Worktag Only must be Yes or No (when populated)
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Name'                                              sheet
     , 'MATCH'                                                     rule_type
     , 'worktag_only'                                              col
     , n.supplier_id                                               supplier_id
     , n.worktag_only                                              detail
     , 'Worktag Only must be either "Yes" or "No".'                message
  FROM workday_supplier_name                                       n
 WHERE n.worktag_only IS NOT NULL
   AND TRIM(n.worktag_only) != ''
   AND n.worktag_only NOT IN ('Yes', 'No')
;

-- ----------------------------------------------------------------------------
-- ENSURE_DATA: If supplier_change_source populated, supplier_source required
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Name'                                                      sheet
     , 'ENSURE_DATA'                                                        rule_type
     , 'supplier_source'                                                    col
     , n.supplier_id                                                        supplier_id
     , n.supplier_change_source                                             detail
     , 'If Supplier Change Source is populated, Supplier Source must also be populated.' message
  FROM workday_supplier_name                                                n
 WHERE n.supplier_change_source IS NOT NULL
   AND TRIM(n.supplier_change_source) != ''
   AND (n.supplier_source IS NULL OR TRIM(n.supplier_source) = '')
;

-- ----------------------------------------------------------------------------
-- ENSURE_DATA: If external_entity_id populated, supplier_source required
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Name'                                                           sheet
     , 'ENSURE_DATA'                                                             rule_type
     , 'supplier_source'                                                         col
     , n.supplier_id                                                             supplier_id
     , n.external_entity_id                                                      detail
     , 'If External Entity ID is populated, Supplier Source must also be populated.' message
  FROM workday_supplier_name                                                     n
 WHERE n.external_entity_id IS NOT NULL
   AND TRIM(n.external_entity_id) != ''
   AND (n.supplier_source IS NULL OR TRIM(n.supplier_source) = '')
;
