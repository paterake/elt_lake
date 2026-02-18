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
--        - 08-32-00  is HMRC VAT (Citibank), not Co-operative Bank
--        - 08-32-10  is HMRC National Insurance (Citibank)
--        - 23-05-80  is Metro Bank, not Barclays
--        - 23-14-70  is Wise, not Barclays
--        - 23-05-05  is Stripe, not Barclays
--        - 40-47-xx  is First Direct, not HSBC retail
--        - 40-12-xx  is M&S Bank, not HSBC retail
--        - 60-83-71  is Starling Bank, not NatWest
--        - 60-84-07  is Chase UK (JP Morgan), not NatWest
--        - 16-57-10  is Cater Allen (Santander Group), not RBS
--        - 16-52-21  is Cumberland Building Society, not RBS
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
        , ('01', 'National Westminster Bank (NatWest)', 'NatWest Group',
           'clearing',
           'Primary NatWest retail and branch range.')
        -- 02 and 03 are not used as primary bank identifiers in the modern system
        , ('02', 'National Westminster Bank (NatWest)', 'NatWest Group',
           'clearing',
           'Secondary NatWest operational range.')
        , ('03', 'National Westminster Bank (NatWest)', 'NatWest Group',
           'clearing',
           'Secondary NatWest operational range.')
        -- 04: Fintech / PSP range — individually sub-allocated
        , ('04', 'Various (Fintech / PSP — see notes)', NULL,
           'psp-allocated',
           'Sub-allocated by Bacs to individual fintechs. Key sub-ranges: '
           || '04-00-04 Monzo, 04-29-09 Revolut, 04-00-75 Modulr Finance, '
           || '04-00-03 Prepay Technologies (PPS), 04-06-05 ClearBank. '
           || 'No single bank owns this prefix. Must use full sort code lookup.')
        , ('05', 'Yorkshire Bank (now Virgin Money)',  'Virgin Money / CYBG',
           'clearing',
           'Yorkshire Bank range; now part of Virgin Money following CYBG/VM merger (2020).')
        , ('06', 'Nationwide Building Society',        'Nationwide',
           'clearing',
           'Nationwide primary range.')
        , ('07', 'Nationwide Building Society',        'Nationwide',
           'clearing',
           '07-00 to 07-49 Nationwide. Upper sub-ranges may be allocated to other PSPs.')
        , ('08', 'Co-operative Bank',                  'Co-operative Bank',
           'clearing',
           'Primary Co-op Bank range. Notable exceptions: '
           || '08-32-00 HMRC VAT (Citibank), 08-32-10 HMRC NI (Citibank). '
           || '08-60 to 08-61 and 08-90 to 08-99 are operational sub-ranges.')
        , ('09', 'Santander UK',                       'Santander Group',
           'clearing',
           '09-00 to 09-19 Santander UK. Inherited from Alliance & Leicester (merged 2010). '
           || 'Some 09-01-xx ranges remain associated with legacy A&L accounts.')
        , ('10', 'Clydesdale Bank (now Virgin Money)', 'Virgin Money / CYBG',
           'clearing',
           '10-00 to 10-79 Clydesdale Bank range; now Virgin Money.')
        , ('11', 'Halifax / Bank of Scotland',         'Lloyds Banking Group',
           'clearing',
           'Halifax and Bank of Scotland retail range. Part of Lloyds Banking Group since 2009.')
        , ('12', 'Clydesdale Bank (now Virgin Money)', 'Virgin Money / CYBG',
           'clearing',
           '12-00 to 12-69 Clydesdale Bank. Now Virgin Money.')
        , ('13', 'Lloyds Bank / Bank of Scotland',     'Lloyds Banking Group',
           'clearing',
           'Bank of Scotland operational range, now Lloyds Banking Group.')
        , ('14', 'Lloyds Bank / Bank of Scotland',     'Lloyds Banking Group',
           'clearing',
           'Bank of Scotland operational range, now Lloyds Banking Group.')
        , ('15', 'Royal Bank of Scotland (RBS/NatWest)', 'NatWest Group',
           'clearing',
           'RBS primary range. 15-80 is part of RBS since 1923. '
           || '15-98 to 15-99 are sub-allocated operational codes.')
        , ('16', 'Royal Bank of Scotland (RBS/NatWest)', 'NatWest Group',
           'clearing',
           'RBS secondary range. Notable exceptions: '
           || '16-00-38 Drummonds Bank (RBS subsidiary), '
           || '16-52-21 Cumberland Building Society, '
           || '16-57-10 Cater Allen Private Bank (Santander Group).')
        , ('17', 'Royal Bank of Scotland (RBS/NatWest)', 'NatWest Group',
           'clearing',
           'RBS operational range.')
        , ('18', 'Clydesdale Bank (now Virgin Money)', 'Virgin Money / CYBG',
           'clearing',
           'Clydesdale Bank Scotland range; now Virgin Money.')
        , ('19', 'Royal Bank of Scotland (RBS/NatWest)', 'NatWest Group',
           'clearing',
           'RBS/Ulster Bank operational range including some Northern Ireland sub-ranges.')
        -- ====================================================================
        -- 20-29: Barclays Bank
        -- ====================================================================
        , ('20', 'Barclays Bank',                      'Barclays Group',
           'clearing',
           'Barclays primary range. Originally allocated as ''2'' pre-1957.')
        , ('21', 'Barclays Bank',                      'Barclays Group',
           'clearing',
           'Barclays secondary range.')
        , ('22', 'Barclays Bank',                      'Barclays Group',
           'clearing',
           'Barclays secondary range.')
        , ('23', 'Barclays Bank (range owner; many sub-allocated)', 'Barclays Group',
           'clearing',
           'Barclays sponsoring range with many PSP sub-allocations. Key exceptions: '
           || '23-05-80 Metro Bank, 23-14-70 Wise (TransferWise), '
           || '23-05-05 Stripe, 23-69-72 Prepay Technologies, '
           || '23-59-54 Newcastle Building Society, 23-32-72 Pockit, '
           || '23-00-88 VFX Financial, 23-22-21 Fire Financial Services. '
           || 'Full sort code lookup required for accurate identification.')
        , ('24', 'Barclays Bank',                      'Barclays Group',
           'clearing',
           'Barclays secondary range.')
        , ('25', 'Barclays Bank',                      'Barclays Group',
           'clearing',
           'Barclays secondary range.')
        , ('26', 'Barclays Bank',                      'Barclays Group',
           'clearing',
           'Barclays secondary range.')
        , ('27', 'Barclays Bank',                      'Barclays Group',
           'clearing',
           'Barclays secondary range.')
        , ('28', 'Barclays Bank',                      'Barclays Group',
           'clearing',
           'Barclays secondary range.')
        , ('29', 'Barclays Bank',                      'Barclays Group',
           'clearing',
           'Barclays secondary range.')
        -- ====================================================================
        -- 30-39: Lloyds Bank
        -- ====================================================================
        , ('30', 'Lloyds Bank',                        'Lloyds Banking Group',
           'clearing',
           'Lloyds primary retail range. Originally allocated as ''3'' pre-1957. '
           || '30-00-66 Arbuthnot Latham, 30-00-83 Al Rayan Bank, 30-02-48 FinecoBank UK.')
        , ('31', 'Lloyds Bank',                        'Lloyds Banking Group',
           'clearing',
           'Lloyds secondary range.')
        , ('32', 'Lloyds Bank',                        'Lloyds Banking Group',
           'clearing',
           'Lloyds secondary range.')
        , ('33', 'Lloyds Bank',                        'Lloyds Banking Group',
           'clearing',
           'Lloyds secondary range.')
        , ('34', 'Lloyds Bank',                        'Lloyds Banking Group',
           'clearing',
           'Lloyds secondary range.')
        , ('35', 'Lloyds Bank',                        'Lloyds Banking Group',
           'clearing',
           'Lloyds secondary range.')
        , ('36', 'Lloyds Bank',                        'Lloyds Banking Group',
           'clearing',
           'Lloyds secondary range.')
        , ('37', 'Lloyds Bank',                        'Lloyds Banking Group',
           'clearing',
           'Lloyds secondary range.')
        , ('38', 'Lloyds Bank',                        'Lloyds Banking Group',
           'clearing',
           'Lloyds secondary range.')
        , ('39', 'Lloyds Bank',                        'Lloyds Banking Group',
           'clearing',
           'Lloyds secondary range.')
        -- ====================================================================
        -- 40-49: HSBC (formerly Midland Bank)
        -- ====================================================================
        , ('40', 'HSBC Bank',                          'HSBC Group',
           'clearing',
           'HSBC primary range. Originally Midland Bank (''4'' pre-1957, then 40). '
           || 'Key sub-allocations: 40-47-xx First Direct, 40-12-xx M&S Bank, '
           || '40-64-05 Tesco Bank, 40-64-25 Virgin Money, 40-64-37 Marcus by Goldman Sachs, '
           || '40-63-01 Coventry Building Society, 40-63-77 Cynergy Bank, '
           || '40-60-80 CashFlows, 40-51-78 Jyske Bank Gibraltar, '
           || '49-99-79 Deutsche Bank.')
        , ('41', 'HSBC Bank',                          'HSBC Group',
           'clearing',
           'HSBC secondary range.')
        , ('42', 'HSBC Bank',                          'HSBC Group',
           'clearing',
           'HSBC secondary range.')
        , ('43', 'HSBC Bank',                          'HSBC Group',
           'clearing',
           'HSBC secondary range.')
        , ('44', 'HSBC Bank',                          'HSBC Group',
           'clearing',
           'HSBC secondary range.')
        , ('45', 'HSBC Bank',                          'HSBC Group',
           'clearing',
           'HSBC secondary range.')
        , ('46', 'HSBC Bank',                          'HSBC Group',
           'clearing',
           'HSBC secondary range.')
        , ('47', 'HSBC Bank',                          'HSBC Group',
           'clearing',
           'HSBC secondary range.')
        , ('48', 'HSBC Bank',                          'HSBC Group',
           'clearing',
           'HSBC secondary range.')
        , ('49', 'HSBC Bank (incl. Deutsche Bank sub-range)', 'HSBC Group',
           'clearing',
           'HSBC range; 49-99-79 to 49-99-99 allocated to Deutsche Bank.')
        -- ====================================================================
        -- 50-59: Bank of Scotland / Lloyds Banking Group (Scotland)
        -- ====================================================================
        , ('50', 'Bank of Scotland',                   'Lloyds Banking Group',
           'clearing',
           'Bank of Scotland Scotland range.')
        , ('51', 'Bank of Scotland',                   'Lloyds Banking Group',
           'clearing',
           'Bank of Scotland Scotland range.')
        , ('52', 'Bank of Scotland',                   'Lloyds Banking Group',
           'clearing',
           'Bank of Scotland Scotland range.')
        , ('53', 'Bank of Scotland',                   'Lloyds Banking Group',
           'clearing',
           'Bank of Scotland Scotland range.')
        , ('54', 'Bank of Scotland',                   'Lloyds Banking Group',
           'clearing',
           'Bank of Scotland Scotland range.')
        , ('55', 'Bank of Scotland',                   'Lloyds Banking Group',
           'clearing',
           'Bank of Scotland Scotland range.')
        , ('56', 'Bank of Scotland',                   'Lloyds Banking Group',
           'clearing',
           'Bank of Scotland Scotland range.')
        , ('57', 'Bank of Scotland',                   'Lloyds Banking Group',
           'clearing',
           'Bank of Scotland Scotland range.')
        , ('58', 'Bank of Scotland',                   'Lloyds Banking Group',
           'clearing',
           'Bank of Scotland Scotland range.')
        , ('59', 'Bank of Scotland',                   'Lloyds Banking Group',
           'clearing',
           'Bank of Scotland Scotland range.')
        -- ====================================================================
        -- 60-72: NatWest Group (incl. many PSP sub-allocations at 60-83/84)
        -- ====================================================================
        , ('60', 'National Westminster Bank (NatWest)', 'NatWest Group',
           'clearing',
           'NatWest primary range. Key sub-allocations: '
           || '60-83-71 Starling Bank, 60-84-07 Chase UK (JP Morgan), '
           || '60-83-12 Atom Bank, 60-83-14 Gibraltar International Bank, '
           || '60-83-66 Fidor Bank UK, 60-84-00 Zopa, '
           || '60-01-73 Reliance Bank Limited.')
        , ('61', 'National Westminster Bank (NatWest)', 'NatWest Group',
           'clearing',
           'NatWest secondary range.')
        , ('62', 'National Westminster Bank (NatWest)', 'NatWest Group',
           'clearing',
           'NatWest secondary range.')
        , ('63', 'National Westminster Bank (NatWest)', 'NatWest Group',
           'clearing',
           'NatWest secondary range.')
        , ('64', 'National Westminster Bank (NatWest)', 'NatWest Group',
           'clearing',
           'NatWest secondary range.')
        , ('65', 'National Westminster Bank (NatWest)', 'NatWest Group',
           'clearing',
           'NatWest secondary range.')
        , ('66', 'National Westminster Bank (NatWest)', 'NatWest Group',
           'clearing',
           'NatWest secondary range.')
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
        -- 77: Lloyds / TSB (former TSB branches)
        -- ====================================================================
        , ('77', 'Lloyds Bank / TSB Bank',             'Lloyds Banking Group / TSB',
           'clearing',
           '77-00 to 77-44 and 77-46 to 77-99. Former TSB branches. '
           || 'When TSB demerged from Lloyds in 2013, some 77-xx branches went to TSB, '
           || 'some stayed with Lloyds — both banks share this prefix range. '
           || 'Full sort code lookup required to distinguish Lloyds from TSB.')
        -- ====================================================================
        -- 80-89: Scotland (separate clearing system until 1985)
        -- ====================================================================
        , ('80', 'Bank of Scotland',                   'Lloyds Banking Group',
           'clearing-scotland',
           'Bank of Scotland Scotland clearing range.')
        , ('81', 'Bank of Scotland',                   'Lloyds Banking Group',
           'clearing-scotland',
           'Bank of Scotland Scotland clearing range.')
        , ('82', 'Clydesdale Bank (now Virgin Money)', 'Virgin Money / CYBG',
           'clearing-scotland',
           'Clydesdale Bank Scotland clearing range.')
        , ('83', 'Clydesdale Bank (now Virgin Money)', 'Virgin Money / CYBG',
           'clearing-scotland',
           'Clydesdale Bank Scotland clearing range (formerly separate institution).')
        , ('84', 'Bank of Scotland',                   'Lloyds Banking Group',
           'clearing-scotland',
           'Bank of Scotland Scotland clearing range (formerly separate institution).')
        , ('85', 'Bank of Scotland',                   'Lloyds Banking Group',
           'clearing-scotland',
           'Bank of Scotland Scotland clearing range.')
        , ('86', 'Clydesdale Bank (now Virgin Money)', 'Virgin Money / CYBG',
           'clearing-scotland',
           'Clydesdale Bank Scotland clearing range.')
        , ('87', 'TSB Bank (formerly TSB Scotland)',   'TSB / Lloyds Banking Group',
           'clearing-scotland',
           'Former TSB Scotland range (merged with TSB/Lloyds 1995). '
           || 'Now administered under Lloyds Banking Group.')
        , ('88', 'Bank of Scotland',                   'Lloyds Banking Group',
           'clearing-scotland',
           'Bank of Scotland Scotland clearing range.')
        , ('89', 'Lloyds Bank / Bank of Scotland',     'Lloyds Banking Group',
           'clearing-scotland',
           '89-00 to 89-29 Lloyds operational range (formerly separate institution).')
        -- ====================================================================
        -- 90-98: Northern Ireland
        -- ====================================================================
        , ('90', 'Ulster Bank (now Danske Bank NI area)', 'NatWest Group / Danske',
           'clearing-northern-ireland',
           'Northern Ireland clearing range. Registered with IPSO/BPFI. '
           || 'Ulster Bank sort codes in NI begin 98-xx-xx.')
        , ('91', 'First Trust Bank (formerly Allied Irish Banks NI)', 'AIB Group',
           'clearing-northern-ireland',
           'Formerly Belfast Banking Company (merged 1970). '
           || 'Now First Trust Bank (AIB Group).')
        , ('92', 'Bank of Ireland (UK)',                'Bank of Ireland Group',
           'clearing-northern-ireland',
           'Bank of Ireland UK Northern Ireland range.')
        , ('93', 'AIB Group (NI) / various',           'AIB Group',
           'clearing-northern-ireland',
           'AIB group NI range; some sub-ranges allocated to other institutions.')
        , ('94', 'Danske Bank (formerly Northern Bank)', 'Danske Bank Group',
           'clearing-northern-ireland',
           'Formerly Northern Bank; rebranded Danske Bank in 2012. '
           || 'Former Clydesdale Bank NI also in this range.')
        , ('95', 'Santander UK (formerly Alliance & Leicester NI)', 'Santander Group',
           'clearing-northern-ireland',
           'NI operational range.')
        , ('98', 'Ulster Bank',                        'NatWest Group',
           'clearing-northern-ireland',
           'Ulster Bank primary Northern Ireland retail range.')
) AS t(sort_code_prefix, bank_name_primary, banking_group, prefix_type, notes)
;