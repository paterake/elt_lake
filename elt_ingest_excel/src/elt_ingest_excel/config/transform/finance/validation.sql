-- ============================================================================
-- VALIDATION RESULTS TABLE
-- ============================================================================
DROP TABLE IF EXISTS validation_results
;
CREATE TABLE validation_results (
    validation_type VARCHAR
  , table_name      VARCHAR
  , data_count      BIGINT
)
;

-- Source table count
INSERT INTO validation_results
SELECT 'record_count', 'src_fin_supplier', COUNT(*) FROM src_fin_supplier
;

-- Record counts by workday table
INSERT INTO validation_results
SELECT 'record_count', 'workday_supplier_name', COUNT(*) FROM workday_supplier_name
;
INSERT INTO validation_results
SELECT 'record_count', 'workday_supplier_groups', COUNT(*) FROM workday_supplier_groups
;
INSERT INTO validation_results
SELECT 'record_count', 'workday_supplier_alternate_name', COUNT(*) FROM workday_supplier_alternate_name
;
INSERT INTO validation_results
SELECT 'record_count', 'workday_supplier_currencies', COUNT(*) FROM workday_supplier_currencies
;
INSERT INTO validation_results
SELECT 'record_count', 'workday_supplier_tax', COUNT(*) FROM workday_supplier_tax
;
INSERT INTO validation_results
SELECT 'record_count', 'workday_supplier_payment', COUNT(*) FROM workday_supplier_payment
;
INSERT INTO validation_results
SELECT 'record_count', 'workday_supplier_procurement', COUNT(*) FROM workday_supplier_procurement
;
INSERT INTO validation_results
SELECT 'record_count', 'workday_supplier_company_restrictions', COUNT(*) FROM workday_supplier_company_restrictions
;
INSERT INTO validation_results
SELECT 'record_count', 'workday_supplier_settlement_account', COUNT(*) FROM workday_supplier_settlement_account
;
INSERT INTO validation_results
SELECT 'record_count', 'workday_supplier_intermediary_account', COUNT(*) FROM workday_supplier_intermediary_account
;
INSERT INTO validation_results
SELECT 'record_count', 'workday_supplier_address', COUNT(*) FROM workday_supplier_address
;
INSERT INTO validation_results
SELECT 'record_count', 'workday_supplier_phone', COUNT(*) FROM workday_supplier_phone
;
INSERT INTO validation_results
SELECT 'record_count', 'workday_supplier_email', COUNT(*) FROM workday_supplier_email
;

-- Data quality checks
INSERT INTO validation_results
SELECT 'data_quality', 'orphan_groups', COUNT(*)
  FROM workday_supplier_groups g
  LEFT JOIN workday_supplier_name n ON g.supplier_id = n.supplier_id
 WHERE n.supplier_id IS NULL
;
INSERT INTO validation_results
SELECT 'data_quality', 'missing_required_supplier_name', COUNT(*)
  FROM workday_supplier_name
 WHERE supplier_id IS NULL OR supplier_name IS NULL
;
INSERT INTO validation_results
SELECT 'data_quality', 'missing_required_currencies', COUNT(*)
  FROM workday_supplier_currencies
 WHERE supplier_id IS NULL OR accepted_currencies_plus IS NULL
;
INSERT INTO validation_results
SELECT 'data_quality', 'invalid_email_addresses', COUNT(*)
  FROM src_fin_supplier
 WHERE email_to_address IS NOT NULL
   AND email_to_address !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
;

COMMIT
;
