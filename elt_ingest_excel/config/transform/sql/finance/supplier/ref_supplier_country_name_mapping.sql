DROP TABLE IF EXISTS ref_supplier_country_name_mapping
;
-- Maps dirty source country names to canonical country_code
CREATE TABLE ref_supplier_country_name_mapping
    AS
SELECT * FROM (VALUES
    -- Argentina
    ('ARGENTINA',               'AR'),
    ('Argentina',               'AR'),

    -- Australia
    ('AUSTRALIA',               'AU'),
    ('Australia',               'AU'),

    -- Austria
    ('AUSTRIA',                 'AT'),
    ('Austria',                 'AT'),

    -- Belgium
    ('BELGIUM',                 'BE'),

    -- Bermuda
    ('Bermuda',                 'BM'),

    -- Bosnia and Herzegovina
    ('BOSNIA AND HERZEGOVINA',  'BA'),

    -- Brazil
    ('BRAZIL',                  'BR'),

    -- Canada (including typo)
    ('CANADA',                  'CA'),
    ('CANANDA',                 'CA'),  -- typo
    ('Canada',                  'CA'),

    -- Cayman Islands
    ('Cayman Islands',          'KY'),

    -- Channel Islands (Jersey/Guernsey - map to Jersey)
    ('Channel Islands',         'JE'),

    -- China
    ('CHINA',                   'CN'),

    -- Croatia
    ('CROATIA',                 'HR'),
    ('Croatia',                 'HR'),

    -- Cyprus
    ('CYPRUS',                  'CY'),
    ('Cyprus',                  'CY'),

    -- Czech Republic
    ('CZECH REPUBLIC',          'CZ'),

    -- Denmark
    ('DENMARK',                 'DK'),
    ('Denmark',                 'DK'),

    -- Dominican Republic
    ('DOMINICAN REPUBLIC',      'DO'),

    -- Estonia
    ('Estonia',                 'EE'),

    -- Finland (including Helsinki city)
    ('FINLAND',                 'FI'),
    ('Helsinki',                'FI'),  -- city in Finland

    -- France
    ('FRANCE',                  'FR'),
    ('France',                  'FR'),

    -- Georgia
    ('GEORGIA',                 'GE'),

    -- Germany
    ('GERMANY',                 'DE'),
    ('Germany',                 'DE'),

    -- Greece
    ('GREECE',                  'GR'),

    -- Hungary
    ('HUNGARY',                 'HU'),

    -- Iceland
    ('ICELAND',                 'IS'),

    -- India
    ('INDIA',                   'IN'),

    -- Indonesia
    ('INDONESIA',               'ID'),

    -- Ireland
    ('IRELAND',                 'IE'),
    ('Ireland',                 'IE'),

    -- Israel
    ('ISRAEL',                  'IL'),

    -- Italy
    ('ITALY',                   'IT'),

    -- Isle of Man
    ('Isle Of Man',             'IM'),

    -- Jamaica
    ('JAMAICA',                 'JM'),

    -- Japan
    ('JAPAN',                   'JP'),

    -- Kazakhstan
    ('KAZAKHSTAN',              'KZ'),

    -- Latvia
    ('Latvia',                  'LV'),

    -- Lesotho
    ('LESOTHO',                 'LS'),

    -- Lithuania
    ('LITHUANIA',               'LT'),

    -- Malaysia
    ('MALAYSIA',                'MY'),
    ('Malaysia',                'MY'),

    -- Malta
    ('MALTA',                   'MT'),
    ('Malta',                   'MT'),

    -- Netherlands (including typo NETHERLAND)
    ('NETHERLAND',              'NL'),
    ('NETHERLANDS',             'NL'),
    ('Netherlands',             'NL'),

    -- New Zealand
    ('NEW ZEALAND',             'NZ'),

    -- Norway
    ('NORWAY',                  'NO'),
    ('Norway',                  'NO'),

    -- Philippines
    ('PHILIPPINES',             'PH'),

    -- Poland (including typo POL;AND)
    ('POL;AND',                 'PL'),  -- typo
    ('POLAND',                  'PL'),
    ('Poland',                  'PL'),

    -- Portugal
    ('PORTUGAL',                'PT'),
    ('Portugal',                'PT'),

    -- Qatar
    ('QATAR',                   'QA'),

    -- Romania (including Ilfov county)
    ('Romania',                 'RO'),
    ('Ilfov',                   'RO'),  -- county in Romania

    -- Saudi Arabia
    ('Saudi Arabia',            'SA'),

    -- Senegal
    ('SENEGAL',                 'SN'),

    -- Serbia
    ('SERBIA',                  'RS'),

    -- Singapore
    ('Singapore',               'SG'),

    -- Slovakia
    ('SLOVAKIA',                'SK'),

    -- Slovenia
    ('SLOVENIA',                'SI'),

    -- South Africa
    ('SOUTH AFRICA',            'ZA'),
    ('South Africa',            'ZA'),

    -- Spain
    ('SPAIN',                   'ES'),
    ('Spain',                   'ES'),

    -- Sweden
    ('SWEDEN',                  'SE'),
    ('Sweden',                  'SE'),

    -- Switzerland
    ('SWITZERLAND',             'CH'),
    ('Switzerland',             'CH'),

    -- Thailand
    ('THAILAND',                'TH'),
    ('Thailand',                'TH'),

    -- Turkey
    ('TURKEY',                  'TR'),

    -- Ukraine
    ('UKRAINE',                 'UA'),

    -- United Arab Emirates
    ('UNITED ARAB EMIRATES',    'AE'),
    ('United Arab Emirates',    'AE'),

    -- United Kingdom (including regions, typos, abbreviations)
    ('ENGLAND',                 'GB'),
    ('England',                 'GB'),
    ('Great Britain',           'GB'),
    ('LONDON',                  'GB'),  -- city
    ('MIDDX',                   'GB'),  -- Middlesex abbreviation
    ('Northern Ireland',        'GB'),
    ('Scotland',                'GB'),
    ('UK',                      'GB'),
    ('UNITED KINGDOM',          'GB'),
    ('UNITED KINGDON',          'GB'),  -- typo
    ('UNITEDKINGDOM',           'GB'),  -- no space
    ('United Kingdom',          'GB'),
    ('Wales',                   'GB'),

    -- United States (including abbreviations)
    ('UNITED STATES',           'US'),
    ('USA',                     'US'),
    ('United States',           'US'),

    -- Uruguay
    ('URUGUAY',                 'UY')

) AS t(source_country_name, country_code)
;
