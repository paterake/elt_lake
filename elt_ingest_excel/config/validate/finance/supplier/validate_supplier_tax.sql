-- ============================================================================
-- VALIDATE: Supplier Tax
-- Source table: workday_supplier_tax
-- VBA rules: Match (cross-tab), Duplicatecolumn, EnsureDataMultipleColumns,
--            Match (Yes/No), Date
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
       'Supplier Tax'                                                   sheet
     , 'CROSS_TAB'                                                     rule_type
     , 'supplier_id'                                                   col
     , t.supplier_id                                                   supplier_id
     , t.supplier_id                                                   detail
     , 'Supplier ID must be listed first on the Supplier Name tab.'    message
  FROM workday_supplier_tax                                            t
  LEFT OUTER JOIN
       workday_supplier_name                                           n
         ON  n.supplier_id                                             = t.supplier_id
 WHERE n.supplier_id IS NULL
;

-- ----------------------------------------------------------------------------
-- DUPLICATE: Business Entity Tax ID must be unique (when populated)
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Tax'                                                          sheet
     , 'DUPLICATE'                                                            rule_type
     , 'business_entity_tax_id'                                               col
     , t.supplier_id                                                          supplier_id
     , t.business_entity_tax_id                                               detail
     , 'Business Entity Tax ID must be unique and cannot be duplicated.'      message
  FROM workday_supplier_tax                                                   t
 WHERE t.business_entity_tax_id IS NOT NULL
   AND t.business_entity_tax_id IN
       (
         SELECT d.business_entity_tax_id
           FROM workday_supplier_tax                                          d
          WHERE d.business_entity_tax_id IS NOT NULL
          GROUP BY d.business_entity_tax_id
         HAVING COUNT(*) > 1
       )
;

-- ----------------------------------------------------------------------------
-- DUPLICATE: Tax ID must be unique (when populated)
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Tax'                                                          sheet
     , 'DUPLICATE'                                                            rule_type
     , 'tax_id'                                                               col
     , t.supplier_id                                                          supplier_id
     , t.tax_id                                                               detail
     , 'The provided Tax ID must be unique.'                                  message
  FROM workday_supplier_tax                                                   t
 WHERE t.tax_id IS NOT NULL
   AND t.tax_id IN
       (
         SELECT d.tax_id
           FROM workday_supplier_tax                                          d
          WHERE d.tax_id IS NOT NULL
          GROUP BY d.tax_id
         HAVING COUNT(*) > 1
       )
;

-- ----------------------------------------------------------------------------
-- MATCH: Primary Tax ID must be Yes or No (when populated)
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Tax'                                                        sheet
     , 'MATCH'                                                              rule_type
     , 'primary_tax_id'                                                     col
     , t.supplier_id                                                        supplier_id
     , t.primary_tax_id                                                     detail
     , 'The Primary Tax ID column must be populated with either "Yes" or "No".' message
  FROM workday_supplier_tax                                                 t
 WHERE t.primary_tax_id IS NOT NULL
   AND TRIM(t.primary_tax_id) != ''
   AND t.primary_tax_id NOT IN ('Yes', 'No')
;

-- ----------------------------------------------------------------------------
-- MATCH: Transaction Tax ID must be Yes or No (when populated)
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Tax'                                                          sheet
     , 'MATCH'                                                                rule_type
     , 'transaction_tax_id'                                                   col
     , t.supplier_id                                                          supplier_id
     , t.transaction_tax_id                                                   detail
     , 'The Transaction Tax ID column must be populated with either "Yes" or "No".' message
  FROM workday_supplier_tax                                                   t
 WHERE t.transaction_tax_id IS NOT NULL
   AND TRIM(t.transaction_tax_id) != ''
   AND t.transaction_tax_id NOT IN ('Yes', 'No')
;

-- ----------------------------------------------------------------------------
-- MATCH: IRS 1099 Supplier must be Yes or No (when populated)
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Tax'                                                          sheet
     , 'MATCH'                                                                rule_type
     , 'irs_1099_supplier'                                                    col
     , t.supplier_id                                                          supplier_id
     , t.irs_1099_supplier                                                    detail
     , 'The IRS 1099 Supplier column must be populated with either "Yes" or "No".' message
  FROM workday_supplier_tax                                                   t
 WHERE t.irs_1099_supplier IS NOT NULL
   AND TRIM(t.irs_1099_supplier) != ''
   AND t.irs_1099_supplier NOT IN ('Yes', 'No')
;

-- ----------------------------------------------------------------------------
-- ENSURE_DATA: If any tax ID field populated, all required fields must be set
-- Required group: tax_id, tax_id_type, primary_tax_id, tax_id_country
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Tax'                                                                    sheet
     , 'ENSURE_DATA'                                                                    rule_type
     , 'tax_id / tax_id_type / primary_tax_id / tax_id_country'                        col
     , t.supplier_id                                                                    supplier_id
     , COALESCE(t.tax_id, t.tax_id_type, t.primary_tax_id, t.tax_id_country)           detail
     , 'If any of Tax ID, Tax ID Type, Primary Tax ID, Tax ID Country is populated, all must be populated.' message
  FROM workday_supplier_tax                                                             t
 WHERE (
           t.tax_id         IS NOT NULL
        OR t.tax_id_type    IS NOT NULL
        OR t.primary_tax_id IS NOT NULL
        OR t.tax_id_country IS NOT NULL
       )
   AND NOT
       (
           t.tax_id         IS NOT NULL AND TRIM(t.tax_id)         != ''
       AND t.tax_id_type    IS NOT NULL AND TRIM(t.tax_id_type)    != ''
       AND t.primary_tax_id IS NOT NULL AND TRIM(t.primary_tax_id) != ''
       AND t.tax_id_country IS NOT NULL AND TRIM(t.tax_id_country) != ''
       )
;
