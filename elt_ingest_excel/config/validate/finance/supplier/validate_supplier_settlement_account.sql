-- ============================================================================
-- VALIDATE: Supplier Settlement Account
-- Source table: workday_supplier_settlement_account
-- VBA rules: Match (cross-tab), Missing, Match (account type/currency),
--            Duplicatecolumn, bankaccountvalidations
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
       'Supplier Settlement Account'                                    sheet
     , 'CROSS_TAB'                                                     rule_type
     , 'supplier_id'                                                   col
     , a.supplier_id                                                   supplier_id
     , a.supplier_id                                                   detail
     , 'Supplier ID must be listed first on the Supplier Name tab.'    message
  FROM workday_supplier_settlement_account                             a
  LEFT OUTER JOIN
       workday_supplier_name                                           n
         ON  n.supplier_id                                             = a.supplier_id
 WHERE n.supplier_id IS NULL
;

-- ----------------------------------------------------------------------------
-- DUPLICATE: Settlement Bank Account ID must be unique (when populated)
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Settlement Account'                                                    sheet
     , 'DUPLICATE'                                                                     rule_type
     , 'settlement_bank_account_id'                                                    col
     , a.supplier_id                                                                   supplier_id
     , a.settlement_bank_account_id                                                    detail
     , 'Settlement Bank Account ID must be unique and cannot be duplicated.'           message
  FROM workday_supplier_settlement_account                                             a
 WHERE a.settlement_bank_account_id IS NOT NULL
   AND a.settlement_bank_account_id IN
       (
         SELECT d.settlement_bank_account_id
           FROM workday_supplier_settlement_account                                    d
          WHERE d.settlement_bank_account_id IS NOT NULL
          GROUP BY d.settlement_bank_account_id
         HAVING COUNT(*) > 1
       )
;

-- ----------------------------------------------------------------------------
-- MISSING: Bank Country is required
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Settlement Account'                                    sheet
     , 'MISSING'                                                       rule_type
     , 'bank_country'                                                  col
     , a.supplier_id                                                   supplier_id
     , NULL                                                            detail
     , 'Bank Country is required.'                                     message
  FROM workday_supplier_settlement_account                             a
 WHERE a.bank_country IS NULL
    OR TRIM(a.bank_country) = ''
;

-- ----------------------------------------------------------------------------
-- MISSING: Currency is required
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Settlement Account'                                    sheet
     , 'MISSING'                                                       rule_type
     , 'currency'                                                      col
     , a.supplier_id                                                   supplier_id
     , NULL                                                            detail
     , 'Currency is a required column.'                                message
  FROM workday_supplier_settlement_account                             a
 WHERE a.currency IS NULL
    OR TRIM(a.currency) = ''
;

-- ----------------------------------------------------------------------------
-- FORMAT: Currency must be a 3-letter ISO code
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Settlement Account'                                          sheet
     , 'FORMAT'                                                              rule_type
     , 'currency'                                                            col
     , a.supplier_id                                                         supplier_id
     , a.currency                                                            detail
     , 'Currency must match a valid ISO 4217 currency code (3 uppercase letters).' message
  FROM workday_supplier_settlement_account                                   a
 WHERE a.currency IS NOT NULL
   AND TRIM(a.currency) != ''
   AND NOT regexp_matches(TRIM(a.currency), '^[A-Z]{3}$')
;

-- ----------------------------------------------------------------------------
-- MISSING: Bank Account Type is required
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Settlement Account'                                    sheet
     , 'MISSING'                                                       rule_type
     , 'bank_account_type'                                             col
     , a.supplier_id                                                   supplier_id
     , NULL                                                            detail
     , 'Bank Account Type is required.'                                message
  FROM workday_supplier_settlement_account                             a
 WHERE a.bank_account_type IS NULL
    OR TRIM(a.bank_account_type) = ''
;

-- ----------------------------------------------------------------------------
-- MATCH: Bank Account Type must be Checking or Savings
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Settlement Account'                                                    sheet
     , 'MATCH'                                                                        rule_type
     , 'bank_account_type'                                                            col
     , a.supplier_id                                                                  supplier_id
     , a.bank_account_type                                                            detail
     , 'Bank Account Type must match one of the drop-down values: "Checking", "Savings".' message
  FROM workday_supplier_settlement_account                                            a
 WHERE a.bank_account_type IS NOT NULL
   AND TRIM(a.bank_account_type) != ''
   AND a.bank_account_type NOT IN ('Checking', 'Savings')
;

-- ----------------------------------------------------------------------------
-- BANK_ACCOUNT: UK GBP accounts must have either account number or IBAN
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Settlement Account'                                                    sheet
     , 'BANK_ACCOUNT'                                                                 rule_type
     , 'bank_account_number / iban'                                                   col
     , a.supplier_id                                                                  supplier_id
     , a.bank_country || ' / ' || COALESCE(a.currency, 'NULL')                       detail
     , 'UK GBP accounts must have a Bank Account Number or IBAN populated.'          message
  FROM workday_supplier_settlement_account                                            a
 WHERE a.bank_country                                                                 = 'United Kingdom'
   AND a.currency                                                                     = 'GBP'
   AND (a.bank_account_number IS NULL OR TRIM(a.bank_account_number) = '')
   AND (a.iban IS NULL OR TRIM(a.iban) = '')
;

-- ----------------------------------------------------------------------------
-- BANK_ACCOUNT: UK GBP accounts should have a sort code (routing_number_bank_code)
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Settlement Account'                                                   sheet
     , 'BANK_ACCOUNT'                                                                rule_type
     , 'routing_number_bank_code'                                                    col
     , a.supplier_id                                                                 supplier_id
     , a.bank_account_number                                                         detail
     , 'UK GBP accounts should have a sort code (Routing Number/Bank Code).'        message
  FROM workday_supplier_settlement_account                                           a
 WHERE a.bank_country                                                                = 'United Kingdom'
   AND a.currency                                                                    = 'GBP'
   AND (a.bank_account_number IS NOT NULL AND TRIM(a.bank_account_number) != '')
   AND (a.routing_number_bank_code IS NULL OR TRIM(a.routing_number_bank_code) = '')
;

-- ----------------------------------------------------------------------------
-- CROSS_TAB: Currency should match Supplier Currencies tab
-- ----------------------------------------------------------------------------
INSERT INTO validation_supplier_issues
SELECT
       'Supplier Settlement Account'                                                   sheet
     , 'CROSS_TAB'                                                                   rule_type
     , 'currency'                                                                    col
     , a.supplier_id                                                                 supplier_id
     , a.currency || ' vs ' || COALESCE(c.accepted_currencies_plus, 'none')         detail
     , 'Settlement Account currency does not match Supplier Currencies tab.'         message
  FROM workday_supplier_settlement_account                                           a
  LEFT OUTER JOIN
       workday_supplier_currencies                                                   c
         ON  c.supplier_id                                                           = a.supplier_id
        AND  c.accepted_currencies_plus                                              = a.currency
 WHERE a.currency IS NOT NULL
   AND c.supplier_id IS NULL
;
