DROP TABLE IF EXISTS ref_worker_type_mapping
;
-- Maps Okta user_type and department_1 values to canonical worker types
-- Rules:
--   • 'Supplier Staff' = Default for all external/human workers (no source evidence for sole traders exists)
--   • NULL = Non-human identities or values requiring exclusion from staff-type classification
--   • 'Sole Trader Staff' = Not used (requires explicit contract/tax evidence not present in source data)
CREATE TABLE ref_worker_type_mapping
    AS
SELECT * FROM (VALUES
    -- user_type mappings
    ('user_type', 'Casual',                     'Supplier Staff'),
    ('user_type', 'Contractors',                'Supplier Staff'),
    ('user_type', 'FA External Contractor',     'Supplier Staff'),
    ('user_type', 'Fixed Term',                 'Supplier Staff'),
    ('user_type', 'Permanent',                  'Supplier Staff'),
    ('user_type', 'Third Party',                'Supplier Staff'),
    ('user_type', 'third party',                'Supplier Staff'),
    ('user_type', 'SERVICE_ACCOUNT',            'EXCLUDE'),  -- EXCLUDE: non-human identity
    ('user_type', 'Service Account',            'EXCLUDE'),  -- EXCLUDE: non-human identity
    ('user_type', 'service account',            'EXCLUDE'),  -- EXCLUDE: non-human identity
    
    -- department_1 mappings: identifiable vendor/supplier companies
    ('department_1', 'Advantage',                  'Supplier Staff'),
    ('department_1', 'Cognizant',                  'Supplier Staff'),
    ('department_1', 'Consultant',                 'Supplier Staff'),
    ('department_1', 'FSP',                        'Supplier Staff'),
    ('department_1', 'First Response Group',       'Supplier Staff'),
    ('department_1', 'Innovate IT',                'Supplier Staff'),
    ('department_1', 'Orion',                      'Supplier Staff'),
    ('department_1', 'Securitas',                  'Supplier Staff'),
    ('department_1', 'Statsports',                 'Supplier Staff'),
    ('department_1', 'Two Circle',                 'Supplier Staff'),
    ('department_1', 'littlethief',                'Supplier Staff'),
    ('department_1', 'real-wireless',              'Supplier Staff'),
    
    -- department_1 mappings: internal-sounding but in contingent context (treated as supplier staff pending validation)
    ('department_1', 'Board & Council',            'Supplier Staff'),
    ('department_1', 'Chair',                      'Supplier Staff'),
    ('department_1', 'Chair''s Assistant',         'Supplier Staff'),
    ('department_1', 'County',                     'Supplier Staff'),
    ('department_1', 'NLS Leagues',                'Supplier Staff'),
    ('department_1', 'National Leagues(FAS Users)','Supplier Staff'),
    
    -- department_1 mappings: EXCLUDE non-human identities
    ('department_1', 'service account',            'EXCLUDE')   -- EXCLUDE: non-human identity

) AS t(source_column, source_value, target_value)
;