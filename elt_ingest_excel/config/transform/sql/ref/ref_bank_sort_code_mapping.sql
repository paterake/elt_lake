DROP TABLE IF EXISTS ref_bank_sort_code_mapping
;
-- ============================================================================
-- UK Bank Sort Code Reference
-- ============================================================================
-- IMPORTANT NOTES:
--   1. Major banks (Barclays, HSBC, Lloyds, NatWest etc.) have thousands of
--      sort codes — one per branch historically, plus operational codes. Entries
--      here represent specific operational / payroll / direct debit sort codes,
--      not a complete branch listing.
--   2. Sort code ownership can change. Always validate against the official BACS
--      EISCD directory for production payroll or payment processing use.
--      Free lookup: https://www.sortcodes.co.uk/sort-code-checker
--   3. The sort_code_purpose column indicates the known use of each sort code:
--        'operational'  - central/operational code used for payroll/BACS/CHAPS
--        'retail'       - customer-facing account sort code
--        'government'   - HMRC or other public sector use
--        'defunct'      - institution has left UK market; code may be reassigned
-- ============================================================================
CREATE TABLE ref_bank_sort_code_mapping
    AS
SELECT
       *
  FROM (VALUES
        -- NB: sort codes stored without hyphens; format as XX-XX-XX for display

        -- Traditional / High Street Banks
          ('GB', '202678', 'Barclays Bank',                          'operational')  -- 20-xx-xx range = Barclays
        , ('GB', '401276', 'HSBC Bank',                              'operational')  -- 40-xx-xx range = Midland/HSBC
        , ('GB', '774926', 'Lloyds Bank',                            'operational')  -- 77-xx-xx = Lloyds (incl. former TSB branches)
        , ('GB', '110001', 'Halifax (Bank of Scotland)',              'operational')  -- 11-xx-xx = Halifax/BoS
        , ('GB', '166300', 'Royal Bank of Scotland',                  'operational')  -- 16-xx-xx = RBS
        , ('GB', '606004', 'National Westminster Bank (NatWest)',      'operational')  -- 60-xx-xx = NatWest group

        -- Building Societies
        , ('GB', '070436', 'Nationwide Building Society',             'operational')

        -- Challenger / Digital Banks
        , ('GB', '040004', 'Monzo Bank',                             'retail')
        , ('GB', '608371', 'Starling Bank',                          'retail')
        , ('GB', '042909', 'Revolut Bank',                           'retail')       -- Revolut's own sort code since UK banking licence (2024)
        , ('GB', '040075', 'Modulr Finance',                         'operational')  -- Modulr's own sort code; previously used by some Revolut products

        -- Payment / FX Services
        , ('GB', '231470', 'Wise (formerly TransferWise)',            'operational')  -- rebranded Feb 2021; sort code still registered as TransferWise Ltd in BACS EISCD

        -- Metro & Specialist Banks
        , ('GB', '230580', 'Metro Bank',                             'retail')
        , ('GB', '609104', 'Standard Chartered Bank',                'operational')

        -- Prepay / E-Money Institutions
        , ('GB', '236972', 'Prepay Technologies',                    'operational')
        , ('GB', '087199', 'APS Financial',                          'operational')

        -- Government
        , ('GB', '083210', 'Government Banking (HMRC Direct Taxes)', 'government')

        -- Santander
        , ('GB', '090128', 'Santander UK',                           'operational')  -- corrected: registered as Santander UK plc, not "Santander Bank"

        -- Additional key institutions (examples; not an exhaustive BACS list)
        , ('GB', '100000', 'Bank of England',                        'operational')
        , ('GB', '089249', 'The Co-operative Bank',                  'retail')
        , ('GB', '300083', 'Al Rayan Bank',                          'retail')
        , ('GB', '165810', 'Triodos Bank UK Ltd',                    'retail')
        , ('GB', '185008', 'Citibank NA',                            'operational')
        , ('GB', '070030', 'Nationwide Building Society',            'retail')
        , ('GB', '040610', 'CB Payments Ltd',                        'operational')
        , ('GB', '040676', 'ClearBank Limited',                      'operational')
        , ('GB', '041307', 'Clear Junction Limited',                 'operational')
        , ('GB', '608384', 'Contis Financial Services Limited',      'operational')
        , ('GB', '231486', 'Payoneer Europe Limited',                'operational')
        , ('GB', '050005', 'Virgin Money',                           'retail')
        , ('GB', '950121', 'Northern Bank Limited T/A Danske Bank',  'retail')

        -- Defunct / Withdrawn from UK Market
        , ('GB', '040026', 'N26 Bank (DEFUNCT - left UK Feb 2020)',   'defunct')     -- N26 withdrew from UK; sort code may be reassigned - do not use for payments

) AS t(country_code, sort_code, bank_name, sort_code_purpose)
;
