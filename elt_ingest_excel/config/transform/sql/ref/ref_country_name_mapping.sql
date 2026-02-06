DROP TABLE IF EXISTS ref_country_name_mapping
;
-- Maps dirty source country names (uppercase) to canonical country_code
-- Join using UPPER(TRIM(source_country_name))
CREATE TABLE ref_country_name_mapping
    AS
SELECT * FROM (VALUES
    ('ABU DHABI',               'AE'),  -- UAE city
    ('ALBANIA',                 'AL'),
    ('ALGERIA',                 'DZ'),
    ('AMSTERDAM',               'NL'),  -- city in Netherlands
    ('ARGENTINA',               'AR'),
    ('AUSTRALIA',               'AU'),
    ('AUSTRIA',                 'AT'),
    ('AUSTRIA,',                'AT'),  -- trailing comma
    ('BELGIUM',                 'BE'),
    ('BERMUDA',                 'BM'),
    ('BOSNIA AND HERZEGOVINA',  'BA'),
    ('BRAZIL',                  'BR'),
    ('BULGARIA',                'BG'),
    ('CAMEROON',                'CM'),
    ('CANADA',                  'CA'),
    ('CANANDA',                 'CA'),  -- typo
    ('CAYMAN ISLANDS',          'KY'),
    ('CHANNEL ISLANDS',         'JE'),
    ('CHILE',                   'CL'),
    ('CHINA',                   'CN'),
    ('COSTA RICA',              'CR'),
    ('COTE D''IVOIRE',          'CI'),  -- escaped apostrophe
    ('CROATIA',                 'HR'),
    ('CYPRUS',                  'CY'),
    ('CZECH REP',               'CZ'),  -- abbreviation
    ('CZECH REPUBLIC',          'CZ'),
    ('DENMARK',                 'DK'),
    ('DOMINICAN REPUBLIC',      'DO'),
    ('ECUADOR',                 'EC'),
    ('ENGLAND',                 'GB'),
    ('ESTONIA',                 'EE'),
    ('FINLAND',                 'FI'),
    ('FRANCE',                  'FR'),
    ('FRANCE,',                 'FR'),  -- trailing comma
    ('GEORGIA',                 'GE'),
    ('GERMANY',                 'DE'),
    ('GERMANY,',                'DE'),  -- trailing comma
    ('GIBRALTAR',               'GI'),
    ('GREAT BRITAIN',           'GB'),
    ('GREECE',                  'GR'),
    ('GUERNSEY',                'GG'),
    ('HELSINKI',                'FI'),  -- city in Finland
    ('HONG KONG',               'HK'),
    ('HONG KONG (SAR)',         'HK'),
    ('HONG KONG,',              'HK'),  -- trailing comma
    ('HUNGARY',                 'HU'),
    ('ICELAND',                 'IS'),
    ('ILFOV',                   'RO'),  -- county in Romania
    ('INDIA',                   'IN'),
    ('INDONESIA',               'ID'),
    ('IRELAND',                 'IE'),
    ('ISLE OF MAN',             'IM'),
    ('ISRAEL',                  'IL'),
    ('ITALY',                   'IT'),
    ('IVORY COAST',             'CI'),
    ('JAMAICA',                 'JM'),
    ('JAPAN',                   'JP'),
    ('JERSEY',                  'JE'),
    ('KAZAKHSTAN',              'KZ'),
    ('KOREA',                   'KR'),
    ('LATVIA',                  'LV'),
    ('LESOTHO',                 'LS'),
    ('LITHUANIA',               'LT'),
    ('LONDON',                  'GB'),  -- city
    ('LUXEMBOURG',              'LU'),
    ('MACEDONIA, FYRO',         'MK'),
    ('MALAYSIA',                'MY'),
    ('MALTA',                   'MT'),
    ('MEXICO',                  'MX'),
    ('MIDDX',                   'GB'),  -- Middlesex abbreviation
    ('MONACO',                  'MC'),
    ('MOROCCO',                 'MA'),
    ('NETHERLAND',              'NL'),  -- typo
    ('NETHERLANDS',             'NL'),
    ('NEW ZEALAND',             'NZ'),
    ('NIGERIA',                 'NG'),
    ('NORTHERN IRELAND',        'GB'),
    ('NORWAY',                  'NO'),
    ('NORWAY,',                 'NO'),  -- trailing comma
    ('OTHER 1',                 NULL),  -- unknown
    ('PARAGUAY',                'PY'),
    ('PHILIPPINES',             'PH'),
    ('POL;AND',                 'PL'),  -- typo
    ('POLAND',                  'PL'),
    ('PORTUGAL',                'PT'),
    ('PUERTO RICO',             'PR'),
    ('QATAR',                   'QA'),
    ('ROMANIA',                 'RO'),
    ('SAUDI ARABIA',            'SA'),
    ('SCOTLAND',                'GB'),
    ('SENEGAL',                 'SN'),
    ('SERBIA',                  'RS'),
    ('SINGAPORE',               'SG'),
    ('SLOVAKIA',                'SK'),
    ('SLOVENIA',                'SI'),
    ('SOUTH AFRICA',            'ZA'),
    ('SPAIN',                   'ES'),
    ('SWEDEN',                  'SE'),
    ('SWITZERLAND',             'CH'),
    ('SWITZERLAND,',            'CH'),  -- trailing comma
    ('THAILAND',                'TH'),
    ('THE NETHERLANDS',         'NL'),
    ('TRINIDAD AND TOBAGO',     'TT'),
    ('TURKEY',                  'TR'),
    ('UAE',                     'AE'),
    ('UK',                      'GB'),
    ('UKRAINE',                 'UA'),
    ('UNITED ARAB EMIRATES',    'AE'),
    ('UNITED KINGDOM',          'GB'),
    ('UNITED KINGDON',          'GB'),  -- typo
    ('UNITED STATES',           'US'),
    ('UNITEDKINGDOM',           'GB'),  -- no space
    ('URUGUAY',                 'UY'),
    ('USA',                     'US'),
    ('WALES',                   'GB')

) AS t(source_country_name, country_code)
;
