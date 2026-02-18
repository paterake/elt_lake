DROP TABLE IF EXISTS ref_country
;
CREATE TABLE ref_country
    AS
SELECT * FROM (VALUES
    ('AE', 'AR', 'AED', '+971', 'Other', 'United Arab Emirates'),
    ('AL', 'SQ', 'ALL', '+355', 'Other', 'Albania'),
    ('AR', 'ES', 'ARS', '+54',  'Other', 'Argentina'),
    ('AT', 'DE', 'EUR', '+43',  'VAT',   'Austria'),
    ('AU', 'EN', 'AUD', '+61',  'Other', 'Australia'),
    ('BA', 'BS', 'BAM', '+387', 'Other', 'Bosnia and Herzegovina'),
    ('BE', 'NL', 'EUR', '+32',  'VAT',   'Belgium'),
    ('BG', 'BG', 'BGN', '+359', 'Other', 'Bulgaria'),
    ('BM', 'EN', 'BMD', '+1',   'Other', 'Bermuda'),
    ('BR', 'PT', 'BRL', '+55',  'Other', 'Brazil'),
    ('CA', 'EN', 'CAD', '+1',   'Other', 'Canada'),
    ('CH', 'DE', 'CHF', '+41',  'Other', 'Switzerland'),
    ('CI', 'FR', 'XOF', '+225', 'Other', 'Côte d''Ivoire'),
    ('CL', 'ES', 'CLP', '+56',  'Other', 'Chile'),
    ('CM', 'FR', 'XAF', '+237', 'Other', 'Cameroon'),
    ('CN', 'ZH', 'CNY', '+86',  'Other', 'China'),
    ('CR', 'ES', 'CRC', '+506', 'Other', 'Costa Rica'),
    ('CY', 'EL', 'EUR', '+357', 'Other', 'Cyprus'),
    ('CZ', 'CS', 'CZK', '+420', 'Other', 'Czechia'),
    ('DE', 'DE', 'EUR', '+49',  'VAT',   'Germany'),
    ('DK', 'DA', 'DKK', '+45',  'VAT',   'Denmark'),
    ('DO', 'ES', 'DOP', '+1',   'Other', 'Dominican Republic'),
    ('DZ', 'AR', 'DZD', '+213', 'Other', 'Algeria'),
    ('EC', 'ES', 'USD', '+593', 'Other', 'Ecuador'),
    ('EE', 'ET', 'EUR', '+372', 'Other', 'Estonia'),
    ('ES', 'ES', 'EUR', '+34',  'VAT',   'Spain'),
    ('FI', 'FI', 'EUR', '+358', 'VAT',   'Finland'),
    ('FR', 'FR', 'EUR', '+33',  'VAT',   'France'),
    ('GB', 'EN', 'GBP', '+44',  'VAT_UK', 'United Kingdom'),
    ('GE', 'KA', 'GEL', '+995', 'Other', 'Georgia'),
    ('GG', 'EN', 'GBP', '+44',  'Other', 'Guernsey'),
    ('GI', 'EN', 'GIP', '+350', 'Other', 'Gibraltar'),
    ('GR', 'EL', 'EUR', '+30',  'Other', 'Greece'),
    ('HK', 'ZH', 'HKD', '+852', 'Other', 'Hong Kong'),
    ('HR', 'HR', 'EUR', '+385', 'Other', 'Croatia'),
    ('HU', 'HU', 'HUF', '+36',  'Other', 'Hungary'),
    ('ID', 'ID', 'IDR', '+62',  'Other', 'Indonesia'),
    ('IE', 'EN', 'EUR', '+353', 'VAT_IE', 'Ireland'),
    ('IL', 'HE', 'ILS', '+972', 'Other', 'Israel'),
    ('IM', 'EN', 'GBP', '+44',  'Other', 'Isle of Man'),
    ('IN', 'HI', 'INR', '+91',  'Other', 'India'),
    ('IS', 'IS', 'ISK', '+354', 'Other', 'Iceland'),
    ('IT', 'IT', 'EUR', '+39',  'VAT',   'Italy'),
    ('JE', 'EN', 'GBP', '+44',  'Other', 'Jersey'),
    ('JM', 'EN', 'JMD', '+1',   'Other', 'Jamaica'),
    ('JP', 'JA', 'JPY', '+81',  'Other', 'Japan'),
    ('KR', 'KO', 'KRW', '+82',  'Other', 'Korea, Republic of'),
    ('KY', 'EN', 'KYD', '+1',   'Other', 'Cayman Islands'),
    ('KZ', 'KK', 'KZT', '+7',   'Other', 'Kazakhstan'),
    ('LS', 'EN', 'LSL', '+266', 'Other', 'Lesotho'),
    ('LT', 'LT', 'EUR', '+370', 'Other', 'Lithuania'),
    ('LU', 'FR', 'EUR', '+352', 'VAT',   'Luxembourg'),
    ('LV', 'LV', 'EUR', '+371', 'Other', 'Latvia'),
    ('MA', 'AR', 'MAD', '+212', 'Other', 'Morocco'),
    ('MC', 'FR', 'EUR', '+377', 'Other', 'Monaco'),
    ('MK', 'MK', 'MKD', '+389', 'Other', 'North Macedonia'),
    ('MT', 'MT', 'EUR', '+356', 'VAT',   'Malta'),
    ('MX', 'ES', 'MXN', '+52',  'Other', 'Mexico'),
    ('MY', 'MS', 'MYR', '+60',  'Other', 'Malaysia'),
    ('NG', 'EN', 'NGN', '+234', 'Other', 'Nigeria'),
    ('NL', 'NL', 'EUR', '+31',  'VAT',   'Netherlands'),
    ('NO', 'NO', 'NOK', '+47',  'Other', 'Norway'),
    ('NZ', 'EN', 'NZD', '+64',  'Other', 'New Zealand'),
    ('PH', 'TL', 'PHP', '+63',  'Other', 'Philippines'),
    ('PL', 'PL', 'PLN', '+48',  'Other', 'Poland'),
    ('PR', 'ES', 'USD', '+1',   'EIN',   'Puerto Rico'),
    ('PT', 'PT', 'EUR', '+351', 'VAT',   'Portugal'),
    ('PY', 'ES', 'PYG', '+595', 'Other', 'Paraguay'),
    ('QA', 'AR', 'QAR', '+974', 'Other', 'Qatar'),
    ('RO', 'RO', 'RON', '+40',  'Other', 'Romania'),
    ('RS', 'SR', 'RSD', '+381', 'Other', 'Serbia'),
    ('SA', 'AR', 'SAR', '+966', 'Other', 'Saudi Arabia'),
    ('SE', 'SV', 'SEK', '+46',  'VAT',   'Sweden'),
    ('SG', 'EN', 'SGD', '+65',  'Other', 'Singapore'),
    ('SI', 'SL', 'EUR', '+386', 'Other', 'Slovenia'),
    ('SK', 'SK', 'EUR', '+421', 'Other', 'Slovakia'),
    ('SN', 'FR', 'XOF', '+221', 'Other', 'Senegal'),
    ('TH', 'TH', 'THB', '+66',  'Other', 'Thailand'),
    ('TR', 'TR', 'TRY', '+90',  'Other', 'Turkey'),
    ('TT', 'EN', 'TTD', '+1',   'Other', 'Trinidad and Tobago'),
    ('UA', 'UK', 'UAH', '+380', 'Other', 'Ukraine'),
    ('US', 'EN', 'USD', '+1',   'EIN',   'United States of America'),
    ('UY', 'ES', 'UYU', '+598', 'Other', 'Uruguay'),
    ('ZA', 'EN', 'ZAR', '+27',  'Other', 'South Africa')
    -- Additional countries from Excel list with placeholder metadata (to be enriched)
  , ('RU', NULL, NULL, NULL, 'Other', 'Russian Federation')
  , ('TW', NULL, NULL, NULL, 'Other', 'Taiwan')
  , ('VA', NULL, NULL, NULL, 'Other', 'Holy See (Vatican City State)')
  , ('PS', NULL, NULL, NULL, 'Other', 'Palestine')
  , ('MO', NULL, NULL, NULL, 'Other', 'Macao')
  , ('FM', NULL, NULL, NULL, 'Other', 'Micronesia, Federated States of')
  , ('CD', NULL, NULL, NULL, 'Other', 'Congo, Democratic Republic of the')
  , ('CG', NULL, NULL, NULL, 'Other', 'Congo')
  , ('CV', NULL, NULL, NULL, 'Other', 'Cabo Verde')
  , ('LA', NULL, NULL, NULL, 'Other', 'Laos')
  , ('TL', NULL, NULL, NULL, 'Other', 'Timor-Leste')
  , ('AX', NULL, NULL, NULL, 'Other', 'Åland Islands')
  , ('CW', NULL, NULL, NULL, 'Other', 'Curaçao')
  , ('RE', NULL, NULL, NULL, 'Other', 'Reunion')
  , ('BL', NULL, NULL, NULL, 'Other', 'Saint Barthelemy')
  , ('MF', NULL, NULL, NULL, 'Other', 'Saint Martin')
  , ('PM', NULL, NULL, NULL, 'Other', 'Saint Pierre and Miquelon')
  , ('ST', NULL, NULL, NULL, 'Other', 'Sao Tome and Principe')
  , ('SX', NULL, NULL, NULL, 'Other', 'Sint Maarten')
  , ('VI', NULL, NULL, NULL, 'Other', 'U. S. Virgin Islands')
  , ('UM', NULL, NULL, NULL, 'Other', 'United States Minor Outlying Islands')
  , ('XK', NULL, NULL, NULL, 'Other', 'Kosovo')
) AS t(country_code, language_code, currency_code, phone_code, tax_id_type, country_name)
;
