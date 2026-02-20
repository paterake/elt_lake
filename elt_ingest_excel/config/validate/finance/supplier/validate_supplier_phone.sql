-- ============================================================================
-- VALIDATE: Supplier Phone
-- Source table: workday_supplier_phone
-- VBA rules: Match (cross-tab), Duplicatecolumn, Missing, Match (Yes/No),
--            OneSelectionPerInstance, MatchValueorFormat (phone digits by country)
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
       'Supplier Phone'                                               sheet
     , 'CROSS_TAB'                                                  rule_type
     , 'supplier_id'                                                col
     , p.supplier_id                                                supplier_id
     , p.supplier_id                                                detail
     , 'Supplier ID must be listed first on the Supplier Name tab.' message
  FROM workday_supplier_phone                                       p
  LEFT OUTER JOIN
       workday_supplier_name                                        n
         ON  n.supplier_id                                          = p.supplier_id
 WHERE n.supplier_id IS NULL
;

-- ----------------------------------------------------------------------------
-- DUPLICATE: Phone ID must be unique
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Phone'                                                   sheet
     , 'DUPLICATE'                                                       rule_type
     , 'phone_id'                                                        col
     , p.supplier_id                                                     supplier_id
     , p.phone_id                                                        detail
     , 'Phone ID must be unique and cannot be duplicated.'               message
  FROM workday_supplier_phone                                            p
 WHERE p.phone_id IN
       (
         SELECT d.phone_id
           FROM workday_supplier_phone                                   d
          GROUP BY d.phone_id
         HAVING COUNT(*) > 1
       )
;

-- ----------------------------------------------------------------------------
-- MISSING: Phone Device Type is required
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Phone'                                                   sheet
     , 'MISSING'                                                         rule_type
     , 'phone_device_type'                                               col
     , p.supplier_id                                                     supplier_id
     , NULL                                                              detail
     , 'Phone device type is a required field.'                          message
  FROM workday_supplier_phone                                            p
 WHERE p.phone_device_type IS NULL
    OR TRIM(p.phone_device_type) = ''
;

-- ----------------------------------------------------------------------------
-- MISSING: Public flag is required
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Phone'                                                   sheet
     , 'MISSING'                                                         rule_type
     , 'public_flag'                                                     col
     , p.supplier_id                                                     supplier_id
     , NULL                                                              detail
     , 'The public column is a required column.'                         message
  FROM workday_supplier_phone                                            p
 WHERE p.public_flag IS NULL
    OR TRIM(p.public_flag) = ''
;

-- ----------------------------------------------------------------------------
-- MATCH: Public flag must be Yes or No
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Phone'                                                         sheet
     , 'MATCH'                                                                 rule_type
     , 'public_flag'                                                           col
     , p.supplier_id                                                           supplier_id
     , p.public_flag                                                           detail
     , 'The Public column must be populated with either "Yes" or "No".'        message
  FROM workday_supplier_phone                                                  p
 WHERE p.public_flag IS NOT NULL
   AND TRIM(p.public_flag) != ''
   AND p.public_flag NOT IN ('Yes', 'No')
;

-- ----------------------------------------------------------------------------
-- MISSING: Primary flag is required
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Phone'                                                   sheet
     , 'MISSING'                                                         rule_type
     , 'primary_flag'                                                    col
     , p.supplier_id                                                     supplier_id
     , NULL                                                              detail
     , 'The primary column is a required column.'                        message
  FROM workday_supplier_phone                                            p
 WHERE p.primary_flag IS NULL
    OR TRIM(p.primary_flag) = ''
;

-- ----------------------------------------------------------------------------
-- MATCH: Primary flag must be Yes or No
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Phone'                                                         sheet
     , 'MATCH'                                                                 rule_type
     , 'primary_flag'                                                          col
     , p.supplier_id                                                           supplier_id
     , p.primary_flag                                                          detail
     , 'The Primary column must be populated with either "Yes" or "No".'       message
  FROM workday_supplier_phone                                                  p
 WHERE p.primary_flag IS NOT NULL
   AND TRIM(p.primary_flag) != ''
   AND p.primary_flag NOT IN ('Yes', 'No')
;

-- ----------------------------------------------------------------------------
-- ONE_PRIMARY: Each Supplier ID + Use For group must have exactly one primary
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Phone'                                                          sheet
     , 'ONE_PRIMARY'                                                            rule_type
     , 'primary_flag'                                                           col
     , grp.supplier_id                                                          supplier_id
     , 'use_for=' || COALESCE(grp.use_for, 'ALL') || ' primary_count=' || grp.primary_count detail
     , 'One business phone must be marked as primary and one only.'             message
  FROM
       (
         SELECT
                p.supplier_id                                                   supplier_id
              , p.use_for                                                       use_for
              , COUNT(*) FILTER (WHERE p.primary_flag = 'Yes')                 primary_count
           FROM workday_supplier_phone                                          p
          GROUP BY p.supplier_id, p.use_for
         HAVING COUNT(*) FILTER (WHERE p.primary_flag = 'Yes') != 1
       )                                                                        grp
;

-- ----------------------------------------------------------------------------
-- FORMAT: UK phone number must be 4–8 digits (no special characters)
-- Checks concatenated area_code + phone_number against digit-only length
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Phone'                                                          sheet
     , 'FORMAT'                                                                 rule_type
     , 'phone_number'                                                           col
     , p.supplier_id                                                            supplier_id
     , COALESCE(p.area_code, '') || p.phone_number                             detail
     , 'Phone Number must be 4–8 digits for United Kingdom (no special characters).' message
  FROM workday_supplier_phone                                                   p
 WHERE p.phone_country                                                          = 'United Kingdom'
   AND p.phone_number IS NOT NULL
   AND NOT regexp_matches(
             regexp_replace(
               COALESCE(p.area_code, '') || COALESCE(p.phone_number, '')
             , '[^0-9]'
             , ''
             , 'g'
             )
           , '^\d{4,8}$'
       )
;

-- ----------------------------------------------------------------------------
-- FORMAT: Netherlands phone number must be 6–8 digits
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Phone'                                                          sheet
     , 'FORMAT'                                                                 rule_type
     , 'phone_number'                                                           col
     , p.supplier_id                                                            supplier_id
     , COALESCE(p.area_code, '') || p.phone_number                             detail
     , 'Phone Number must be 6–8 digits for Netherlands (no special characters).' message
  FROM workday_supplier_phone                                                   p
 WHERE p.phone_country                                                          = 'Netherlands'
   AND p.phone_number IS NOT NULL
   AND NOT regexp_matches(
             regexp_replace(
               COALESCE(p.area_code, '') || COALESCE(p.phone_number, '')
             , '[^0-9]'
             , ''
             , 'g'
             )
           , '^\d{6,8}$'
       )
;
