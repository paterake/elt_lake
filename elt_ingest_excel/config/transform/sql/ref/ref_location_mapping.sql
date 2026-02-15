DROP TABLE IF EXISTS ref_location_mapping
;
-- Maps Okta location values to 4 canonical locations
-- Rules:
--   • Only 4 valid target locations permitted: Homebased - SGP | Homebased - Wembley | St George's Park | Wembley Stadium
--   • NULL = EXCLUDE from contingent worker population (non-physical locations, external entities, or ambiguous values)
--   • 'County' explicitly excluded per business rule
--   • Cognizant and The FA Group mapped to Wembley Stadium (temporary assumption for testing)
CREATE TABLE ref_location_mapping
    AS
SELECT * FROM (VALUES
    -- Explicit exclusions (map to NULL)
    ('location', 'County',                   NULL),  -- EXPLICIT EXCLUSION per business rule
    ('location', 'Country',                  NULL),  -- EXPLICIT EXCLUSION per requirement
    ('location', '',                         NULL),  -- [BLANK] → EXCLUDE
    ('location', 'Amateur Football Alliance',NULL),  -- External entity → exclude
    ('location', 'Cornwall FA',              NULL),  -- County FA → exclude
    ('location', 'Essex FA',                 NULL),  -- County FA → exclude
    ('location', 'Football Conference',      NULL),  -- External entity → exclude
    ('location', 'Football365',              NULL),  -- Media/vendor → exclude
    
    -- Special mappings per testing requirement
    ('location', 'Cognizant',                'Wembley Stadium'),  -- Vendor staff assumed co-located at HQ
    ('location', 'The FA Group',             'Wembley Stadium'),  -- Org entity mapped to primary HQ
    
    -- Valid canonical mappings
    ('location', 'Homebased - SGP',          'Homebased - SGP'),
    ('location', 'Homebased',                'Homebased - Wembley'),  -- Standardize to canonical form
    ('location', 'Homebased - Wembley',      'Homebased - Wembley'),
    ('location', 'SGP',                      'St George''s Park'),    -- Standardize to canonical form
    ('location', 'St George''s Park',        'St George''s Park'),
    ('location', 'Wembley',                  'Wembley Stadium'),      -- Standardize to canonical form
    ('location', 'Wembley Stadium',          'Wembley Stadium')
) AS t(source_column, source_value, target_value)
;