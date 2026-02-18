DROP TABLE IF EXISTS ref_bank_sort_code_prefix_mapping
;
-- ============================================================================
-- UK Sort Code Prefix → Bank Mapping
-- ============================================================================
-- PURPOSE:
--   Provides a "best effort" bank identification from the first 2 digits of a
--   sort code. Useful for display/labelling purposes only.
--
-- IMPORTANT LIMITATIONS - READ BEFORE USING:
--
--   1. NOT a substitute for EISCD.
--      The only authoritative source for sort code → bank lookup is the
--      EISCD (Extended Industry Sort Code Directory), licensed via Vocalink
--      at ~£2,023+VAT/year. This table is a coarse approximation only.
--
--   2. PREFIX LOOKUP IS INHERENTLY IMPRECISE.
--      The first 2 digits identify the primary clearing bank that "owns" the
--      range, but many sort codes within a range are sub-allocated to other
--      institutions. For example:
--        - 08-32-00  is HMRC VAT (Citibank UK Limited), not Co-operative Bank
--        - 08-32-10  is HMRC National Insurance (Citibank UK Limited)
--        - 23-05-80  is Metro Bank plc, not Barclays
--        - 23-14-70  is Wise (not PRA-regulated; FCA e-money institution), not Barclays
--        - 23-05-05  is Stripe (not PRA-regulated), not Barclays
--        - 40-47-xx  is First Direct (trading name of HSBC UK Bank plc), not HSBC retail
--        - 40-12-xx  is Marks and Spencer Financial Services plc, not HSBC retail
--        - 60-83-71  is Starling Bank Limited, not NatWest
--        - 60-84-07  is J.P. Morgan Europe Limited (Chase UK brand), not NatWest
--        - 16-57-10  is Cater Allen Limited (Santander Group), not RBS
--        - 16-52-21  is Cumberland Building Society (not PRA bank-authorised), not RBS
--
--   3. RANGE SHARING.
--      Some clearing banks act as sponsors for many smaller/foreign banks.
--      The 04-xx-xx range in particular covers dozens of separate fintechs
--      and e-money institutions, each allocated individually.
--
--   4. HISTORICAL MERGERS.
--      Many ranges were inherited through M&A. The bank shown is the current
--      legal owner of the range, not the original allocatee.
--
--   5. THE 04-xx-xx RANGE IS SPECIAL.
--      This range is used by Bacs for non-cheque PSPs (fintechs, e-money
--      institutions). Individual sub-ranges are allocated separately — there
--      is no single "04 = one bank" rule. Key sub-allocations are listed in
--      ref_bank_sort_code_mapping.
--
--   6. SCOTLAND (80-89) AND NORTHERN IRELAND (90-98).
--      These have their own clearing systems and ranges. Scottish ranges
--      were operated separately until 1985.
--
--   7. BANK NAMES.
--      Primary bank names use the official PRA-authorised legal entity names
--      as published in the Bank of England PRA register (February 2026).
--      Some institutions (e.g. Nationwide Building Society, building societies,
--      FCA-only e-money institutions) are not PRA bank-authorised and retain
--      their common names where no PRA entry exists.
--
--   8. CLYDESDALE BANK PLC / VIRGIN MONEY.
--      Clydesdale Bank plc (trading as Virgin Money) was acquired by
--      Nationwide Group in October 2024. The PRA-authorised legal entity
--      remains Clydesdale Bank plc.
--
-- USAGE PATTERN (PostgreSQL example):
--   SELECT bank_name_primary
--   FROM   ref_sort_code_prefix_bank_mapping
--   WHERE  sort_code_prefix = LEFT(REPLACE(:sort_code, '-', ''), 2)
-- ============================================================================
CREATE TABLE ref_bank_sort_code_prefix_mapping
    AS
SELECT *
  FROM (VALUES
        -- sort_code_prefix, bank_name_primary, banking_group, prefix_type, notes
        -- ====================================================================
        -- 00: Non-standard (IBAN-only)
        -- ====================================================================
          ('00', 'Non-standard (IBAN use only)',      NULL,
           'non-standard',
           'Used only within IBANs for incoming Euro transfers. Not valid for domestic UK payments.')
        -- ====================================================================
        -- 01-19: Primarily NatWest/RBS Group, building societies, and others
        -- ====================================================================
        , ('01', 'National Westminster Bank plc', 'NatWest Group',
           'clearing',
           'Primary NatWest retail and branch range.')
        -- 02 and 03 are not used as primary bank identifiers in the modern system
        , ('02', 'National Westminster Bank plc', 'NatWest Group',
           'clearing',
           'Secondary NatWest operational range.')
        , ('03', 'National Westminster Bank plc', 'NatWest Group',
           'clearing',
           'Secondary NatWest operational range.')
        -- 04: Fintech / PSP range — individually sub-allocated
        , ('04', 'Various (Fintech / PSP — see notes)', NULL,
           'psp-allocated',
           'Sub-allocated by Bacs to individual fintechs. Key sub-ranges: '
           || '04-00-04 Monzo Bank Ltd, 04-29-09 Revolut NewCo UK Ltd, '
           || '04-00-75 Modulr Finance (FCA e-money institution), '
           || '04-00-03 Prepay Technologies / PPS (FCA e-money institution), '
           || '04-06-05 ClearBank Limited. '
           || 'No single bank owns this prefix. Must use full sort code lookup.')
        , ('05', 'Clydesdale Bank plc',  'Nationwide Group',
           'clearing',
           'Clydesdale Bank plc range, trading as Virgin Money / Yorkshire Bank. '
           || 'Clydesdale Bank plc acquired by Nationwide Group in October 2024.')
        , ('06', 'Nationwide Building Society',        'Nationwide Group',
           'clearing',
           'Nationwide Building Society primary range. Not PRA bank-authorised; '
           || 'regulated by PRA as a building society.')
        , ('07', 'Nationwide Building Society',        'Nationwide Group',
           'clearing',
           '07-00 to 07-49 Nationwide Building Society. Upper sub-ranges may be '
           || 'allocated to other PSPs.')
        , ('08', 'The Co-operative Bank p.l.c.',       'The Co-operative Bank p.l.c.',
           'clearing',
           'Primary Co-operative Bank range. Notable exceptions: '
           || '08-32-00 HMRC VAT (Citibank UK Limited), '
           || '08-32-10 HMRC NI (Citibank UK Limited). '
           || '08-60 to 08-61 and 08-90 to 08-99 are operational sub-ranges.')
        , ('09', 'Santander UK plc',                   'Santander Group',
           'clearing',
           '09-00 to 09-19 Santander UK plc. Inherited from Alliance & Leicester '
           || '(merged 2010). Some 09-01-xx ranges remain associated with '
           || 'legacy A&L accounts.')
        , ('10', 'Clydesdale Bank plc',                'Nationwide Group',
           'clearing',
           '10-00 to 10-79 Clydesdale Bank plc range, trading as Virgin Money. '
           || 'Acquired by Nationwide Group in October 2024.')
        , ('11', 'Bank of Scotland plc',               'Lloyds Banking Group',
           'clearing',
           'Bank of Scotland plc retail range (includes Halifax brand). '
           || 'Part of Lloyds Banking Group since 2009.')
        , ('12', 'Clydesdale Bank plc',                'Nationwide Group',
           'clearing',
           '12-00 to 12-69 Clydesdale Bank plc, trading as Virgin Money. '
           || 'Acquired by Nationwide Group in October 2024.')
        , ('13', 'Bank of Scotland plc',               'Lloyds Banking Group',
           'clearing',
           'Bank of Scotland plc operational range, now Lloyds Banking Group.')
        , ('14', 'Bank of Scotland plc',               'Lloyds Banking Group',
           'clearing',
           'Bank of Scotland plc operational range, now Lloyds Banking Group.')
        , ('15', 'The Royal Bank of Scotland plc',     'NatWest Group',
           'clearing',
           'The Royal Bank of Scotland plc primary range. 15-80 is part of RBS '
           || 'since 1923. 15-98 to 15-99 are sub-allocated operational codes.')
        , ('16', 'The Royal Bank of Scotland plc',     'NatWest Group',
           'clearing',
           'The Royal Bank of Scotland plc secondary range. Notable exceptions: '
           || '16-00-38 Drummonds Bank (NatWest Group subsidiary), '
           || '16-52-21 Cumberland Building Society (not PRA bank-authorised), '
           || '16-57-10 Cater Allen Limited (Santander Group).')
        , ('17', 'The Royal Bank of Scotland plc',     'NatWest Group',
           'clearing',
           'The Royal Bank of Scotland plc operational range.')
        , ('18', 'Clydesdale Bank plc',                'Nationwide Group',
           'clearing',
           'Clydesdale Bank plc Scotland range. Acquired by Nationwide Group '
           || 'in October 2024.')
        , ('19', 'The Royal Bank of Scotland plc',     'NatWest Group',
           'clearing',
           'The Royal Bank of Scotland plc / Ulster Bank operational range '
           || 'including some Northern Ireland sub-ranges.')
        -- ====================================================================
        -- 20-29: Barclays Bank UK PLC
        -- ====================================================================
        , ('20', 'Barclays Bank UK plc',               'Barclays Group',
           'clearing',
           'Barclays Bank UK plc primary retail range. Originally allocated as '
           || '''2'' pre-1957. Note: Barclays Bank plc is the separate wholesale/'
           || 'international entity within the same group.')
        , ('21', 'Barclays Bank UK plc',               'Barclays Group',
           'clearing',
           'Barclays Bank UK plc secondary range.')
        , ('22', 'Barclays Bank UK plc',               'Barclays Group',
           'clearing',
           'Barclays Bank UK plc secondary range.')
        , ('23', 'Barclays Bank UK plc (range owner; many sub-allocated)', 'Barclays Group',
           'clearing',
           'Barclays Bank UK plc sponsoring range with many PSP sub-allocations. '
           || 'Key exceptions: 23-05-80 Metro Bank plc, '
           || '23-14-70 Wise (FCA e-money institution, not PRA-authorised), '
           || '23-05-05 Stripe (not PRA-authorised), '
           || '23-69-72 Prepay Technologies (FCA e-money institution), '
           || '23-59-54 Newcastle Building Society (not PRA bank-authorised), '
           || '23-32-72 Pockit, 23-00-88 VFX Financial, '
           || '23-22-21 Fire Financial Services. '
           || 'Full sort code lookup required for accurate identification.')
        , ('24', 'Barclays Bank UK plc',               'Barclays Group',
           'clearing',
           'Barclays Bank UK plc secondary range.')
        , ('25', 'Barclays Bank UK plc',               'Barclays Group',
           'clearing',
           'Barclays Bank UK plc secondary range.')
        , ('26', 'Barclays Bank UK plc',               'Barclays Group',
           'clearing',
           'Barclays Bank UK plc secondary range.')
        , ('27', 'Barclays Bank UK plc',               'Barclays Group',
           'clearing',
           'Barclays Bank UK plc secondary range.')
        , ('28', 'Barclays Bank UK plc',               'Barclays Group',
           'clearing',
           'Barclays Bank UK plc secondary range.')
        , ('29', 'Barclays Bank UK plc',               'Barclays Group',
           'clearing',
           'Barclays Bank UK plc secondary range.')
        -- ====================================================================
        -- 30-39: Lloyds Bank PLC
        -- ====================================================================
        , ('30', 'Lloyds Bank plc',                    'Lloyds Banking Group',
           'clearing',
           'Lloyds Bank plc primary retail range. Originally allocated as '
           || '''3'' pre-1957. '
           || 'Notable sub-allocations: 30-00-66 Arbuthnot Latham & Co., Limited, '
           || '30-00-83 Al Rayan Bank plc, 30-02-48 FinecoBank SPA (EEA branch).')
        , ('31', 'Lloyds Bank plc',                    'Lloyds Banking Group',
           'clearing',
           'Lloyds Bank plc secondary range.')
        , ('32', 'Lloyds Bank plc',                    'Lloyds Banking Group',
           'clearing',
           'Lloyds Bank plc secondary range.')
        , ('33', 'Lloyds Bank plc',                    'Lloyds Banking Group',
           'clearing',
           'Lloyds Bank plc secondary range.')
        , ('34', 'Lloyds Bank plc',                    'Lloyds Banking Group',
           'clearing',
           'Lloyds Bank plc secondary range.')
        , ('35', 'Lloyds Bank plc',                    'Lloyds Banking Group',
           'clearing',
           'Lloyds Bank plc secondary range.')
        , ('36', 'Lloyds Bank plc',                    'Lloyds Banking Group',
           'clearing',
           'Lloyds Bank plc secondary range.')
        , ('37', 'Lloyds Bank plc',                    'Lloyds Banking Group',
           'clearing',
           'Lloyds Bank plc secondary range.')
        , ('38', 'Lloyds Bank plc',                    'Lloyds Banking Group',
           'clearing',
           'Lloyds Bank plc secondary range.')
        , ('39', 'Lloyds Bank plc',                    'Lloyds Banking Group',
           'clearing',
           'Lloyds Bank plc secondary range.')
        -- ====================================================================
        -- 40-49: HSBC UK Bank plc (formerly Midland Bank)
        -- ====================================================================
        , ('40', 'HSBC UK Bank plc',                   'HSBC Group',
           'clearing',
           'HSBC UK Bank plc primary range. Originally Midland Bank '
           || '(''4'' pre-1957, then 40). Note: HSBC Bank plc is the separate '
           || 'wholesale/international entity within the same group. '
           || 'Key sub-allocations: '
           || '40-47-xx First Direct (trading name of HSBC UK Bank plc), '
           || '40-12-xx Marks and Spencer Financial Services plc, '
           || '40-64-05 Barclays Bank UK plc (formerly Tesco Bank; acquired 2024), '
           || '40-64-25 Clydesdale Bank plc (Virgin Money brand), '
           || '40-64-37 Goldman Sachs International Bank (Marcus brand), '
           || '40-63-01 Coventry Building Society (not PRA bank-authorised), '
           || '40-63-77 Cynergy Bank plc, '
           || '40-60-80 CashFlows (FCA e-money institution), '
           || '40-51-78 Gibraltar International Bank Limited, '
           || '49-99-79 Deutsche Bank AG.')
        , ('41', 'HSBC UK Bank plc',                   'HSBC Group',
           'clearing',
           'HSBC UK Bank plc secondary range.')
        , ('42', 'HSBC UK Bank plc',                   'HSBC Group',
           'clearing',
           'HSBC UK Bank plc secondary range.')
        , ('43', 'HSBC UK Bank plc',                   'HSBC Group',
           'clearing',
           'HSBC UK Bank plc secondary range.')
        , ('44', 'HSBC UK Bank plc',                   'HSBC Group',
           'clearing',
           'HSBC UK Bank plc secondary range.')
        , ('45', 'HSBC UK Bank plc',                   'HSBC Group',
           'clearing',
           'HSBC UK Bank plc secondary range.')
        , ('46', 'HSBC UK Bank plc',                   'HSBC Group',
           'clearing',
           'HSBC UK Bank plc secondary range.')
        , ('47', 'HSBC UK Bank plc',                   'HSBC Group',
           'clearing',
           'HSBC UK Bank plc secondary range.')
        , ('48', 'HSBC UK Bank plc',                   'HSBC Group',
           'clearing',
           'HSBC UK Bank plc secondary range.')
        , ('49', 'HSBC UK Bank plc (incl. Deutsche Bank AG sub-range)', 'HSBC Group',
           'clearing',
           'HSBC UK Bank plc range; 49-99-79 to 49-99-99 allocated to Deutsche Bank AG.')
        -- ====================================================================
        -- 50-59: Bank of Scotland plc / Lloyds Banking Group (Scotland)
        -- ====================================================================
        , ('50', 'Bank of Scotland plc',               'Lloyds Banking Group',
           'clearing',
           'Bank of Scotland plc Scotland range.')
        , ('51', 'Bank of Scotland plc',               'Lloyds Banking Group',
           'clearing',
           'Bank of Scotland plc Scotland range.')
        , ('52', 'Bank of Scotland plc',               'Lloyds Banking Group',
           'clearing',
           'Bank of Scotland plc Scotland range.')
        , ('53', 'Bank of Scotland plc',               'Lloyds Banking Group',
           'clearing',
           'Bank of Scotland plc Scotland range.')
        , ('54', 'Bank of Scotland plc',               'Lloyds Banking Group',
           'clearing',
           'Bank of Scotland plc Scotland range.')
        , ('55', 'Bank of Scotland plc',               'Lloyds Banking Group',
           'clearing',
           'Bank of Scotland plc Scotland range.')
        , ('56', 'Bank of Scotland plc',               'Lloyds Banking Group',
           'clearing',
           'Bank of Scotland plc Scotland range.')
        , ('57', 'Bank of Scotland plc',               'Lloyds Banking Group',
           'clearing',
           'Bank of Scotland plc Scotland range.')
        , ('58', 'Bank of Scotland plc',               'Lloyds Banking Group',
           'clearing',
           'Bank of Scotland plc Scotland range.')
        , ('59', 'Bank of Scotland plc',               'Lloyds Banking Group',
           'clearing',
           'Bank of Scotland plc Scotland range.')
        -- ====================================================================
        -- 60-72: NatWest Group (incl. many PSP sub-allocations at 60-83/84)
        -- ====================================================================
        , ('60', 'National Westminster Bank plc',      'NatWest Group',
           'clearing',
           'National Westminster Bank plc primary range. Key sub-allocations: '
           || '60-83-71 Starling Bank Limited, '
           || '60-84-07 J.P. Morgan Europe Limited (Chase UK brand), '
           || '60-83-12 Atom Bank plc, '
           || '60-83-14 Gibraltar International Bank Limited, '
           || '60-83-66 FidBank UK Limited (formerly Fidor Bank UK), '
           || '60-84-00 Zopa Bank Limited, '
           || '60-01-73 Reliance Bank Limited.')
        , ('61', 'National Westminster Bank plc',      'NatWest Group',
           'clearing',
           'National Westminster Bank plc secondary range.')
        , ('62', 'National Westminster Bank plc',      'NatWest Group',
           'clearing',
           'National Westminster Bank plc secondary range.')
        , ('63', 'National Westminster Bank plc',      'NatWest Group',
           'clearing',
           'National Westminster Bank plc secondary range.')
        , ('64', 'National Westminster Bank plc',      'NatWest Group',
           'clearing',
           'National Westminster Bank plc secondary range.')
        , ('65', 'National Westminster Bank plc',      'NatWest Group',
           'clearing',
           'National Westminster Bank plc secondary range.')
        , ('66', 'National Westminster Bank plc',      'NatWest Group',
           'clearing',
           'National Westminster Bank plc secondary range.')
        , ('70', 'Various (historically foreign/non-clearing banks)', NULL,
           'legacy',
           'Originally reserved for London offices of non-clearing banks (''walks''). '
           || 'Most reallocated to clearing bank sponsorship by the 1990s. '
           || 'Full sort code lookup required.')
        , ('71', 'Various (historically foreign/non-clearing banks)', NULL,
           'legacy',
           'See prefix 70 notes.')
        , ('72', 'Various (historically foreign/non-clearing banks)', NULL,
           'legacy',
           'See prefix 70 notes.')
        -- ====================================================================
        -- 77: Lloyds Bank plc / TSB Bank plc (former TSB branches)
        -- ====================================================================
        , ('77', 'Lloyds Bank plc / TSB Bank plc',     'Lloyds Banking Group / TSB',
           'clearing',
           '77-00 to 77-44 and 77-46 to 77-99. Former TSB branches. '
           || 'When TSB demerged from Lloyds in 2013, some 77-xx branches went to '
           || 'TSB Bank plc, some stayed with Lloyds Bank plc — both banks share '
           || 'this prefix range. Full sort code lookup required to distinguish '
           || 'Lloyds Bank plc from TSB Bank plc.')
        -- ====================================================================
        -- 80-89: Scotland (separate clearing system until 1985)
        -- ====================================================================
        , ('80', 'Bank of Scotland plc',               'Lloyds Banking Group',
           'clearing-scotland',
           'Bank of Scotland plc Scotland clearing range.')
        , ('81', 'Bank of Scotland plc',               'Lloyds Banking Group',
           'clearing-scotland',
           'Bank of Scotland plc Scotland clearing range.')
        , ('82', 'Clydesdale Bank plc',                'Nationwide Group',
           'clearing-scotland',
           'Clydesdale Bank plc Scotland clearing range. Acquired by Nationwide '
           || 'Group in October 2024.')
        , ('83', 'Clydesdale Bank plc',                'Nationwide Group',
           'clearing-scotland',
           'Clydesdale Bank plc Scotland clearing range (formerly separate '
           || 'institution). Acquired by Nationwide Group in October 2024.')
        , ('84', 'Bank of Scotland plc',               'Lloyds Banking Group',
           'clearing-scotland',
           'Bank of Scotland plc Scotland clearing range (formerly separate '
           || 'institution).')
        , ('85', 'Bank of Scotland plc',               'Lloyds Banking Group',
           'clearing-scotland',
           'Bank of Scotland plc Scotland clearing range.')
        , ('86', 'Clydesdale Bank plc',                'Nationwide Group',
           'clearing-scotland',
           'Clydesdale Bank plc Scotland clearing range. Acquired by Nationwide '
           || 'Group in October 2024.')
        , ('87', 'TSB Bank plc',                       'TSB Bank plc',
           'clearing-scotland',
           'Former TSB Scotland range (merged with TSB/Lloyds 1995). '
           || 'Now administered under TSB Bank plc.')
        , ('88', 'Bank of Scotland plc',               'Lloyds Banking Group',
           'clearing-scotland',
           'Bank of Scotland plc Scotland clearing range.')
        , ('89', 'Bank of Scotland plc',               'Lloyds Banking Group',
           'clearing-scotland',
           '89-00 to 89-29 Lloyds Banking Group operational range (formerly '
           || 'separate institution).')
        -- ====================================================================
        -- 90-98: Northern Ireland
        -- ====================================================================
        , ('90', 'The Royal Bank of Scotland plc',     'NatWest Group',
           'clearing-northern-ireland',
           'Northern Ireland clearing range. Registered with IPSO/BPFI. '
           || 'Ulster Bank (NatWest Group brand in NI) sort codes begin 98-xx-xx. '
           || 'The Royal Bank of Scotland plc is the PRA-authorised legal entity '
           || 'for NatWest Group NI operations.')
        , ('91', 'AIB Group (UK) plc',                 'AIB Group',
           'clearing-northern-ireland',
           'Formerly Belfast Banking Company (merged 1970). '
           || 'Now AIB Group (UK) plc, trading as First Trust Bank in NI.')
        , ('92', 'Bank of Ireland (UK) plc',           'Bank of Ireland Group',
           'clearing-northern-ireland',
           'Bank of Ireland (UK) plc Northern Ireland range.')
        , ('93', 'AIB Group (UK) plc / various',       'AIB Group',
           'clearing-northern-ireland',
           'AIB Group (UK) plc NI range; some sub-ranges allocated to other '
           || 'institutions.')
        , ('94', 'Northern Bank Limited',              'Danske Bank Group',
           'clearing-northern-ireland',
           'Northern Bank Limited, the PRA-authorised UK entity for Danske Bank '
           || 'in Northern Ireland. Rebranded Danske Bank in 2012. '
           || 'Former Clydesdale Bank NI also in this range.')
        , ('95', 'Santander UK plc',                   'Santander Group',
           'clearing-northern-ireland',
           'Santander UK plc NI operational range (formerly Alliance & Leicester NI).')
        , ('98', 'The Royal Bank of Scotland plc',     'NatWest Group',
           'clearing-northern-ireland',
           'Ulster Bank (NatWest Group brand) primary Northern Ireland retail range. '
           || 'The PRA-authorised legal entity is The Royal Bank of Scotland plc.')
) AS t(sort_code_prefix, bank_name_primary, banking_group, prefix_type, notes)
;