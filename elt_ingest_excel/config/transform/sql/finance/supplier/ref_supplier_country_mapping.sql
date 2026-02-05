DROP TABLE IF EXISTS ref_supplier_country_mapping
;
-- Maps dirty source country names/codes to canonical country_code
-- Used to normalise inconsistent source data before joining to ref_supplier_country
-- Structure: name-only entries for name lookup, code-only entries for code fallback
CREATE TABLE ref_supplier_country_mapping
    AS
SELECT * FROM (VALUES
    -- ===========================================
    -- NAME-ONLY MAPPINGS (primary lookup)
    -- ===========================================

    -- Argentina
    ('ARGENTINA',               NULL,   'AR'),
    ('Argentina',               NULL,   'AR'),

    -- Australia
    ('AUSTRALIA',               NULL,   'AU'),
    ('Australia',               NULL,   'AU'),

    -- Austria
    ('AUSTRIA',                 NULL,   'AT'),
    ('Austria',                 NULL,   'AT'),

    -- Belgium
    ('BELGIUM',                 NULL,   'BE'),

    -- Bermuda
    ('Bermuda',                 NULL,   'BM'),

    -- Bosnia and Herzegovina
    ('BOSNIA AND HERZEGOVINA',  NULL,   'BA'),

    -- Brazil
    ('BRAZIL',                  NULL,   'BR'),

    -- Canada (including typo)
    ('CANADA',                  NULL,   'CA'),
    ('CANANDA',                 NULL,   'CA'),  -- typo
    ('Canada',                  NULL,   'CA'),

    -- Cayman Islands
    ('Cayman Islands',          NULL,   'KY'),

    -- Channel Islands (Jersey/Guernsey - map to Jersey)
    ('Channel Islands',         NULL,   'JE'),

    -- China
    ('CHINA',                   NULL,   'CN'),

    -- Croatia
    ('CROATIA',                 NULL,   'HR'),
    ('Croatia',                 NULL,   'HR'),

    -- Cyprus
    ('CYPRUS',                  NULL,   'CY'),
    ('Cyprus',                  NULL,   'CY'),

    -- Czech Republic
    ('CZECH REPUBLIC',          NULL,   'CZ'),

    -- Denmark
    ('DENMARK',                 NULL,   'DK'),
    ('Denmark',                 NULL,   'DK'),

    -- Dominican Republic
    ('DOMINICAN REPUBLIC',      NULL,   'DO'),

    -- Estonia
    ('Estonia',                 NULL,   'EE'),

    -- Finland (including Helsinki city)
    ('FINLAND',                 NULL,   'FI'),
    ('Helsinki',                NULL,   'FI'),  -- city in Finland

    -- France
    ('FRANCE',                  NULL,   'FR'),
    ('France',                  NULL,   'FR'),

    -- Georgia
    ('GEORGIA',                 NULL,   'GE'),

    -- Germany
    ('GERMANY',                 NULL,   'DE'),
    ('Germany',                 NULL,   'DE'),

    -- Greece
    ('GREECE',                  NULL,   'GR'),

    -- Hungary
    ('HUNGARY',                 NULL,   'HU'),

    -- Iceland
    ('ICELAND',                 NULL,   'IS'),

    -- India
    ('INDIA',                   NULL,   'IN'),

    -- Indonesia
    ('INDONESIA',               NULL,   'ID'),

    -- Ireland
    ('IRELAND',                 NULL,   'IE'),
    ('Ireland',                 NULL,   'IE'),

    -- Israel
    ('ISRAEL',                  NULL,   'IL'),

    -- Italy
    ('ITALY',                   NULL,   'IT'),

    -- Isle of Man
    ('Isle Of Man',             NULL,   'IM'),

    -- Jamaica
    ('JAMAICA',                 NULL,   'JM'),

    -- Japan
    ('JAPAN',                   NULL,   'JP'),

    -- Kazakhstan
    ('KAZAKHSTAN',              NULL,   'KZ'),

    -- Latvia
    ('Latvia',                  NULL,   'LV'),

    -- Lesotho
    ('LESOTHO',                 NULL,   'LS'),

    -- Lithuania
    ('LITHUANIA',               NULL,   'LT'),

    -- Malaysia
    ('MALAYSIA',                NULL,   'MY'),
    ('Malaysia',                NULL,   'MY'),

    -- Malta
    ('MALTA',                   NULL,   'MT'),
    ('Malta',                   NULL,   'MT'),

    -- Netherlands (including typo NETHERLAND)
    ('NETHERLAND',              NULL,   'NL'),
    ('NETHERLANDS',             NULL,   'NL'),
    ('Netherlands',             NULL,   'NL'),

    -- New Zealand
    ('NEW ZEALAND',             NULL,   'NZ'),

    -- Norway
    ('NORWAY',                  NULL,   'NO'),
    ('Norway',                  NULL,   'NO'),

    -- Philippines
    ('PHILIPPINES',             NULL,   'PH'),

    -- Poland (including typo POL;AND)
    ('POL;AND',                 NULL,   'PL'),  -- typo
    ('POLAND',                  NULL,   'PL'),
    ('Poland',                  NULL,   'PL'),

    -- Portugal
    ('PORTUGAL',                NULL,   'PT'),
    ('Portugal',                NULL,   'PT'),

    -- Qatar
    ('QATAR',                   NULL,   'QA'),

    -- Romania (including Ilfov county)
    ('Romania',                 NULL,   'RO'),
    ('Ilfov',                   NULL,   'RO'),  -- county in Romania

    -- Saudi Arabia
    ('Saudi Arabia',            NULL,   'SA'),

    -- Senegal
    ('SENEGAL',                 NULL,   'SN'),

    -- Serbia
    ('SERBIA',                  NULL,   'RS'),

    -- Singapore
    ('Singapore',               NULL,   'SG'),

    -- Slovakia
    ('SLOVAKIA',                NULL,   'SK'),

    -- Slovenia
    ('SLOVENIA',                NULL,   'SI'),

    -- South Africa
    ('SOUTH AFRICA',            NULL,   'ZA'),
    ('South Africa',            NULL,   'ZA'),

    -- Spain
    ('SPAIN',                   NULL,   'ES'),
    ('Spain',                   NULL,   'ES'),

    -- Sweden
    ('SWEDEN',                  NULL,   'SE'),
    ('Sweden',                  NULL,   'SE'),

    -- Switzerland
    ('SWITZERLAND',             NULL,   'CH'),
    ('Switzerland',             NULL,   'CH'),

    -- Thailand
    ('THAILAND',                NULL,   'TH'),
    ('Thailand',                NULL,   'TH'),

    -- Turkey
    ('TURKEY',                  NULL,   'TR'),

    -- Ukraine
    ('UKRAINE',                 NULL,   'UA'),

    -- United Arab Emirates
    ('UNITED ARAB EMIRATES',    NULL,   'AE'),
    ('United Arab Emirates',    NULL,   'AE'),

    -- United Kingdom (including regions, typos, abbreviations)
    ('ENGLAND',                 NULL,   'GB'),
    ('England',                 NULL,   'GB'),
    ('Great Britain',           NULL,   'GB'),
    ('LONDON',                  NULL,   'GB'),  -- city
    ('MIDDX',                   NULL,   'GB'),  -- Middlesex abbreviation
    ('Northern Ireland',        NULL,   'GB'),
    ('Scotland',                NULL,   'GB'),
    ('UK',                      NULL,   'GB'),
    ('UNITED KINGDOM',          NULL,   'GB'),
    ('UNITED KINGDON',          NULL,   'GB'),  -- typo
    ('UNITEDKINGDOM',           NULL,   'GB'),  -- no space
    ('United Kingdom',          NULL,   'GB'),
    ('Wales',                   NULL,   'GB'),

    -- United States (including abbreviations)
    ('UNITED STATES',           NULL,   'US'),
    ('USA',                     NULL,   'US'),
    ('United States',           NULL,   'US'),

    -- Uruguay
    ('URUGUAY',                 NULL,   'UY'),

    -- Unknown/Other
    ('OTHER 1',                 NULL,   NULL),  -- unknown mapping

    -- ===========================================
    -- CODE-ONLY MAPPINGS (fallback lookup)
    -- ===========================================
    (NULL,                      'AR',   'AR'),
    (NULL,                      'AU',   'AU'),
    (NULL,                      'BE',   'BE'),
    (NULL,                      'CA',   'CA'),
    (NULL,                      'CH',   'CH'),
    (NULL,                      'DE',   'DE'),
    (NULL,                      'DK',   'DK'),
    (NULL,                      'ES',   'ES'),
    (NULL,                      'FR',   'FR'),
    (NULL,                      'GB',   'GB'),
    (NULL,                      'IE',   'IE'),
    (NULL,                      'LV',   'LV'),
    (NULL,                      'NL',   'NL'),
    (NULL,                      'NZ',   'NZ'),
    (NULL,                      'PL',   'PL'),
    (NULL,                      'SZ',   'CH'),  -- incorrect code for Switzerland
    (NULL,                      'US',   'US')

) AS t(source_country_name, source_country_code, country_code)
;
