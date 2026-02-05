DROP TABLE IF EXISTS ref_customer_country_name_mapping
;
-- Maps dirty source country names (uppercase) to canonical country_code
-- Join using UPPER(TRIM(source_country_name))
CREATE TABLE ref_customer_country_name_mapping
    AS
SELECT * FROM (VALUES
    ('ABU DHABI',               'AE'),  -- UAE city
    ('ALBANIA',                 'AL'),
    ('ALGERIA',                 'DZ'),
    ('AMSTERDAM',               'NL'),  -- city in Netherlands
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
    ('ECUADOR',                 'EC'),
    ('ENGLAND',                 'GB'),
    ('ESTONIA',                 'EE'),
    ('FINLAND',                 'FI'),
    ('FRANCE',                  'FR'),
    ('FRANCE,',                 'FR'),  -- trailing comma
    ('GERMANY',                 'DE'),
    ('GERMANY,',                'DE'),  -- trailing comma
    ('GIBRALTAR',               'GI'),
    ('GREECE',                  'GR'),
    ('GUERNSEY',                'GG'),
    ('HONG KONG',               'HK'),
    ('HONG KONG (SAR)',         'HK'),
    ('HONG KONG,',              'HK'),  -- trailing comma
    ('HUNGARY',                 'HU'),
    ('ICELAND',                 'IS'),
    ('INDIA',                   'IN'),
    ('INDONESIA',               'ID'),
    ('IRELAND',                 'IE'),
    ('ISLE OF MAN',             'IM'),
    ('ISRAEL',                  'IL'),
    ('ITALY',                   'IT'),
    ('IVORY COAST',             'CI'),
    ('JAPAN',                   'JP'),
    ('JERSEY',                  'JE'),
    ('KOREA',                   'KR'),
    ('LATVIA',                  'LV'),
    ('LUXEMBOURG',              'LU'),
    ('MACEDONIA, FYRO',         'MK'),
    ('MALAYSIA',                'MY'),
    ('MALTA',                   'MT'),
    ('MEXICO',                  'MX'),
    ('MONACO',                  'MC'),
    ('MOROCCO',                 'MA'),
    ('NETHERLAND',              'NL'),  -- typo
    ('NETHERLANDS',             'NL'),
    ('NEW ZEALAND',             'NZ'),
    ('NIGERIA',                 'NG'),
    ('NORTHERN IRELAND',        'GB'),
    ('NORWAY',                  'NO'),
    ('NORWAY,',                 'NO'),  -- trailing comma
    ('PARAGUAY',                'PY'),
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
    ('SOUTH AFRICA',            'ZA'),
    ('SPAIN',                   'ES'),
    ('SWEDEN',                  'SE'),
    ('SWITZERLAND',             'CH'),
    ('SWITZERLAND,',            'CH'),  -- trailing comma
    ('THAILAND',                'TH'),
    ('THE NETHERLANDS',         'NL'),
    ('TRINIDAD AND TOBAGO',     'TT'),
    ('UAE',                     'AE'),
    ('UK',                      'GB'),
    ('UNITED ARAB EMIRATES',    'AE'),
    ('UNITED KINGDOM',          'GB'),
    ('UNITED STATES',           'US'),
    ('USA',                     'US'),
    ('WALES',                   'GB')

) AS t(source_country_name, country_code)
;
