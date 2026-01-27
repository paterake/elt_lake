-- ============================================================================
-- VALIDATION QUERIES
-- ============================================================================

-- Source table count
SELECT 'src_fin_supplier' as table_name, COUNT(*) as record_count FROM src_fin_supplier
;

-- Record counts by table
SELECT 'workday_supplier_name' as table_name, COUNT(*) as record_count FROM workday_supplier_name
UNION ALL SELECT 'workday_supplier_groups', COUNT(*) FROM workday_supplier_groups
UNION ALL SELECT 'workday_supplier_alternate_name', COUNT(*) FROM workday_supplier_alternate_name
UNION ALL SELECT 'workday_supplier_currencies', COUNT(*) FROM workday_supplier_currencies
UNION ALL SELECT 'workday_supplier_tax', COUNT(*) FROM workday_supplier_tax
UNION ALL SELECT 'workday_supplier_payment', COUNT(*) FROM workday_supplier_payment
UNION ALL SELECT 'workday_supplier_procurement', COUNT(*) FROM workday_supplier_procurement
UNION ALL SELECT 'workday_supplier_company_restrictions', COUNT(*) FROM workday_supplier_company_restrictions
UNION ALL SELECT 'workday_supplier_settlement_account', COUNT(*) FROM workday_supplier_settlement_account
UNION ALL SELECT 'workday_supplier_intermediary_account', COUNT(*) FROM workday_supplier_intermediary_account
UNION ALL SELECT 'workday_supplier_address', COUNT(*) FROM workday_supplier_address
UNION ALL SELECT 'workday_supplier_phone', COUNT(*) FROM workday_supplier_phone
UNION ALL SELECT 'workday_supplier_email', COUNT(*) FROM workday_supplier_email
ORDER BY table_name
;

-- Data quality checks
SELECT 'Orphan Groups' as check_name, COUNT(*) as issue_count
  FROM workday_supplier_groups g
  LEFT JOIN workday_supplier_name n ON g.supplier_id = n.supplier_id
 WHERE n.supplier_id IS NULL
UNION ALL
SELECT 'Missing Required - Supplier Name', COUNT(*)
  FROM workday_supplier_name
 WHERE supplier_id IS NULL OR supplier_name IS NULL
UNION ALL
SELECT 'Missing Required - Currencies', COUNT(*)
  FROM workday_supplier_currencies
 WHERE supplier_id IS NULL OR accepted_currencies_plus IS NULL
UNION ALL
SELECT 'Invalid Email Addresses', COUNT(*)
  FROM src_fin_supplier
 WHERE email_to_address IS NOT NULL
   AND email_to_address !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
;
