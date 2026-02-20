-- ============================================================================
-- VALIDATE: Supplier Address
-- Source table: workday_supplier_address
-- VBA rules: Match (cross-tab), Duplicatecolumn, Missing, OneSelectionPerInstance,
--            Match (Yes/No flags), addressrequirementsvalidation
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
       'Supplier Address'                                              sheet
     , 'CROSS_TAB'                                                   rule_type
     , 'supplier_id'                                                 col
     , a.supplier_id                                                 supplier_id
     , a.supplier_id                                                 detail
     , 'Supplier ID must be listed first on the Supplier Name tab.'  message
  FROM workday_supplier_address                                      a
  LEFT OUTER JOIN
       workday_supplier_name                                         n
         ON  n.supplier_id                                           = a.supplier_id
 WHERE n.supplier_id IS NULL
;

-- ----------------------------------------------------------------------------
-- DUPLICATE: Address ID must be unique
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Address'                                                  sheet
     , 'DUPLICATE'                                                        rule_type
     , 'address_id'                                                       col
     , a.supplier_id                                                      supplier_id
     , a.address_id                                                       detail
     , 'Address ID must be unique and cannot be duplicated.'              message
  FROM workday_supplier_address                                           a
 WHERE a.address_id IS NOT NULL
   AND a.address_id IN
       (
         SELECT d.address_id
           FROM workday_supplier_address                                  d
          WHERE d.address_id IS NOT NULL
          GROUP BY d.address_id
         HAVING COUNT(*) > 1
       )
;

-- ----------------------------------------------------------------------------
-- MISSING: Country is required
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Address'                                                         sheet
     , 'MISSING'                                                                 rule_type
     , 'country'                                                                 col
     , a.supplier_id                                                             supplier_id
     , NULL                                                                      detail
     , 'Country is a required column and must be populated for the used row.'    message
  FROM workday_supplier_address                                                  a
 WHERE a.country IS NULL
    OR TRIM(a.country) = ''
;

-- ----------------------------------------------------------------------------
-- MISSING: Address Line 1 is required
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Address'                                                         sheet
     , 'MISSING'                                                                 rule_type
     , 'address_line_1'                                                          col
     , a.supplier_id                                                             supplier_id
     , NULL                                                                      detail
     , 'Address Line 1 is a required column and must be populated for the used row.' message
  FROM workday_supplier_address                                                  a
 WHERE a.address_line_1 IS NULL
    OR TRIM(a.address_line_1) = ''
;

-- ----------------------------------------------------------------------------
-- MISSING: Public flag is required
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Address'                                               sheet
     , 'MISSING'                                                       rule_type
     , 'public_flag'                                                   col
     , a.supplier_id                                                   supplier_id
     , NULL                                                            detail
     , 'The public column is a required column.'                       message
  FROM workday_supplier_address                                        a
 WHERE a.public_flag IS NULL
    OR TRIM(a.public_flag) = ''
;

-- ----------------------------------------------------------------------------
-- MATCH: Public flag must be Yes or No
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Address'                                                          sheet
     , 'MATCH'                                                                   rule_type
     , 'public_flag'                                                              col
     , a.supplier_id                                                              supplier_id
     , a.public_flag                                                              detail
     , 'The Public column must be populated with either "Yes" or "No".'           message
  FROM workday_supplier_address                                                   a
 WHERE a.public_flag IS NOT NULL
   AND TRIM(a.public_flag) != ''
   AND a.public_flag NOT IN ('Yes', 'No')
;

-- ----------------------------------------------------------------------------
-- MISSING: Primary flag is required
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Address'                                               sheet
     , 'MISSING'                                                       rule_type
     , 'primary_flag'                                                  col
     , a.supplier_id                                                   supplier_id
     , NULL                                                            detail
     , 'The primary column is a required column.'                      message
  FROM workday_supplier_address                                        a
 WHERE a.primary_flag IS NULL
    OR TRIM(a.primary_flag) = ''
;

-- ----------------------------------------------------------------------------
-- MATCH: Primary flag must be Yes or No
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Address'                                                          sheet
     , 'MATCH'                                                                   rule_type
     , 'primary_flag'                                                             col
     , a.supplier_id                                                              supplier_id
     , a.primary_flag                                                             detail
     , 'The Primary column must be populated with either "Yes" or "No".'          message
  FROM workday_supplier_address                                                   a
 WHERE a.primary_flag IS NOT NULL
   AND TRIM(a.primary_flag) != ''
   AND a.primary_flag NOT IN ('Yes', 'No')
;

-- ----------------------------------------------------------------------------
-- ONE_PRIMARY: Each Supplier ID + Use For group must have exactly one primary
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Address'                                                          sheet
     , 'ONE_PRIMARY'                                                              rule_type
     , 'primary_flag'                                                             col
     , grp.supplier_id                                                            supplier_id
     , 'use_for=' || COALESCE(grp.use_for, 'ALL') || ' primary_count=' || grp.primary_count detail
     , 'One business address must be marked as primary and one only.'             message
  FROM
       (
         SELECT
                a.supplier_id                                                     supplier_id
              , a.use_for                                                         use_for
              , COUNT(*) FILTER (WHERE a.primary_flag = 'Yes')                   primary_count
           FROM workday_supplier_address                                          a
          GROUP BY a.supplier_id, a.use_for
         HAVING COUNT(*) FILTER (WHERE a.primary_flag = 'Yes') != 1
       )                                                                          grp
;

-- ----------------------------------------------------------------------------
-- ADDRESS_REQ: UK addresses should have a Region (county/state)
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Address'                                                          sheet
     , 'ADDRESS_REQ'                                                              rule_type
     , 'region'                                                                   col
     , a.supplier_id                                                              supplier_id
     , a.country                                                                  detail
     , 'Region is recommended for United Kingdom addresses.'                      message
  FROM workday_supplier_address                                                   a
 WHERE a.country                                                                  = 'United Kingdom'
   AND (a.region IS NULL OR TRIM(a.region) = '')
;

-- ----------------------------------------------------------------------------
-- ADDRESS_REQ: UK addresses should have a Postal Code
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Address'                                                          sheet
     , 'ADDRESS_REQ'                                                              rule_type
     , 'postal_code'                                                              col
     , a.supplier_id                                                              supplier_id
     , a.address_line_1                                                           detail
     , 'Postal Code is required for United Kingdom addresses.'                    message
  FROM workday_supplier_address                                                   a
 WHERE a.country                                                                  = 'United Kingdom'
   AND (a.postal_code IS NULL OR TRIM(a.postal_code) = '')
;
