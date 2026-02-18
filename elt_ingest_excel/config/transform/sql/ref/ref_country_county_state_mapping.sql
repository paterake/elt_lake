DROP TABLE IF EXISTS ref_country_county_state_mapping
;
CREATE TABLE ref_country_county_state_mapping
    AS
SELECT
       *
  FROM (VALUES

        -- =====================================================================
        -- United Kingdom (GB) - ONS 2021 Boundaries
        -- =====================================================================

        -- ---------------------------------------------------------------------
        -- England: Non-Metropolitan Counties (current)
        -- ---------------------------------------------------------------------
          ('GB', 'Cambridgeshire',                       'current')
        , ('GB', 'Cumbria',                              'current')
        , ('GB', 'Derbyshire',                           'current')
        , ('GB', 'Devon',                                'current')
        , ('GB', 'Dorset',                               'current')
        , ('GB', 'East Sussex',                          'current')
        , ('GB', 'Essex',                                'current')
        , ('GB', 'Gloucestershire',                      'current')
        , ('GB', 'Hampshire',                            'current')
        , ('GB', 'Hertfordshire',                        'current')
        , ('GB', 'Kent',                                 'current')
        , ('GB', 'Lancashire',                           'current')
        , ('GB', 'Leicestershire',                       'current')
        , ('GB', 'Lincolnshire',                         'current')
        , ('GB', 'Norfolk',                              'current')
        , ('GB', 'North Yorkshire',                      'current')
        , ('GB', 'Nottinghamshire',                      'current')
        , ('GB', 'Oxfordshire',                          'current')
        , ('GB', 'Somerset',                             'current')
        , ('GB', 'Staffordshire',                        'current')
        , ('GB', 'Suffolk',                              'current')
        , ('GB', 'Surrey',                               'current')
        , ('GB', 'Warwickshire',                         'current')
        , ('GB', 'West Sussex',                          'current')
        , ('GB', 'Worcestershire',                       'current')

        -- ---------------------------------------------------------------------
        -- England: Metropolitan Counties (current - retained for statistics)
        -- ---------------------------------------------------------------------
        , ('GB', 'Greater Manchester',                   'current')
        , ('GB', 'Merseyside',                           'current')
        , ('GB', 'South Yorkshire',                      'current')
        , ('GB', 'Tyne and Wear',                        'current')
        , ('GB', 'West Midlands',                        'current')
        , ('GB', 'West Yorkshire',                       'current')

        -- ---------------------------------------------------------------------
        -- England: Unitary Authorities (outside London, current)
        -- ---------------------------------------------------------------------
        , ('GB', 'Bath and North East Somerset',         'current')
        , ('GB', 'Bedford',                              'current')
        , ('GB', 'Blackburn with Darwen',                'current')
        , ('GB', 'Blackpool',                            'current')
        , ('GB', 'Bournemouth, Christchurch and Poole',  'current')
        , ('GB', 'Bracknell Forest',                     'current')
        , ('GB', 'Brighton and Hove',                    'current')
        , ('GB', 'Buckinghamshire',                      'current')
        , ('GB', 'Central Bedfordshire',                 'current')
        , ('GB', 'Cheshire East',                        'current')
        , ('GB', 'Cheshire West and Chester',            'current')
        , ('GB', 'City of Bristol',                      'current')
        , ('GB', 'City of Kingston upon Hull',           'current')
        , ('GB', 'Cornwall',                             'current')
        , ('GB', 'County Durham',                        'current')
        , ('GB', 'County of Herefordshire',              'current')
        , ('GB', 'Darlington',                           'current')
        , ('GB', 'Derby',                                'current')
        , ('GB', 'East Riding of Yorkshire',             'current')
        , ('GB', 'Halton',                               'current')
        , ('GB', 'Hartlepool',                           'current')
        , ('GB', 'Isle of Wight',                        'current')
        , ('GB', 'Isles of Scilly',                      'current')
        , ('GB', 'Leicester',                            'current')
        , ('GB', 'Luton',                                'current')
        , ('GB', 'Medway',                               'current')
        , ('GB', 'Middlesbrough',                        'current')
        , ('GB', 'Milton Keynes',                        'current')
        , ('GB', 'North East Lincolnshire',              'current')
        , ('GB', 'North Lincolnshire',                   'current')
        , ('GB', 'North Northamptonshire',               'current')
        , ('GB', 'North Somerset',                       'current')
        , ('GB', 'Northumberland',                       'current')
        , ('GB', 'Nottingham',                           'current')
        , ('GB', 'Peterborough',                         'current')
        , ('GB', 'Plymouth',                             'current')
        , ('GB', 'Portsmouth',                           'current')
        , ('GB', 'Reading',                              'current')
        , ('GB', 'Redcar and Cleveland',                 'current')
        , ('GB', 'Rutland',                              'current')
        , ('GB', 'Shropshire',                           'current')
        , ('GB', 'Slough',                               'current')
        , ('GB', 'South Gloucestershire',                'current')
        , ('GB', 'Southampton',                          'current')
        , ('GB', 'Southend-on-Sea',                      'current')
        , ('GB', 'Stockton-on-Tees',                     'current')
        , ('GB', 'Stoke-on-Trent',                       'current')
        , ('GB', 'Swindon',                              'current')
        , ('GB', 'Telford and Wrekin',                   'current')
        , ('GB', 'Thurrock',                             'current')
        , ('GB', 'Torbay',                               'current')
        , ('GB', 'Warrington',                           'current')
        , ('GB', 'West Berkshire',                       'current')
        , ('GB', 'West Northamptonshire',                'current')
        , ('GB', 'Wiltshire',                            'current')
        , ('GB', 'Windsor and Maidenhead',               'current')
        , ('GB', 'Wokingham',                            'current')
        , ('GB', 'York',                                 'current')

        -- ---------------------------------------------------------------------
        -- England: London Boroughs (32) + City of London (current)
        -- ---------------------------------------------------------------------
        , ('GB', 'Barking and Dagenham',                 'current')
        , ('GB', 'Barnet',                               'current')
        , ('GB', 'Bexley',                               'current')
        , ('GB', 'Brent',                                'current')
        , ('GB', 'Bromley',                              'current')
        , ('GB', 'Camden',                               'current')
        , ('GB', 'City of London',                       'current')
        , ('GB', 'Croydon',                              'current')
        , ('GB', 'Ealing',                               'current')
        , ('GB', 'Enfield',                              'current')
        , ('GB', 'Greenwich',                            'current')
        , ('GB', 'Hackney',                              'current')
        , ('GB', 'Hammersmith and Fulham',               'current')
        , ('GB', 'Haringey',                             'current')
        , ('GB', 'Harrow',                               'current')
        , ('GB', 'Havering',                             'current')
        , ('GB', 'Hillingdon',                           'current')
        , ('GB', 'Hounslow',                             'current')
        , ('GB', 'Islington',                            'current')
        , ('GB', 'Kensington and Chelsea',               'current')
        , ('GB', 'Kingston upon Thames',                 'current')
        , ('GB', 'Lambeth',                              'current')
        , ('GB', 'Lewisham',                             'current')
        , ('GB', 'Merton',                               'current')
        , ('GB', 'Newham',                               'current')
        , ('GB', 'Redbridge',                            'current')
        , ('GB', 'Richmond upon Thames',                 'current')
        , ('GB', 'Southwark',                            'current')
        , ('GB', 'Sutton',                               'current')
        , ('GB', 'Tower Hamlets',                        'current')
        , ('GB', 'Waltham Forest',                       'current')
        , ('GB', 'Wandsworth',                           'current')
        , ('GB', 'Westminster',                          'current')

        -- ---------------------------------------------------------------------
        -- Wales: 22 Principal Areas (current)
        -- ---------------------------------------------------------------------
        , ('GB', 'Blaenau Gwent',                        'current')
        , ('GB', 'Bridgend',                             'current')
        , ('GB', 'Caerphilly',                           'current')
        , ('GB', 'Cardiff',                              'current')
        , ('GB', 'Carmarthenshire',                      'current')
        , ('GB', 'Ceredigion',                           'current')
        , ('GB', 'Conwy',                                'current')
        , ('GB', 'Denbighshire',                         'current')
        , ('GB', 'Flintshire',                           'current')
        , ('GB', 'Gwynedd',                              'current')
        , ('GB', 'Isle of Anglesey',                     'current')
        , ('GB', 'Merthyr Tydfil',                       'current')
        , ('GB', 'Monmouthshire',                        'current')
        , ('GB', 'Neath Port Talbot',                    'current')
        , ('GB', 'Newport',                              'current')
        , ('GB', 'Pembrokeshire',                        'current')
        , ('GB', 'Powys',                                'current')
        , ('GB', 'Rhondda Cynon Taf',                    'current')
        , ('GB', 'Swansea',                              'current')
        , ('GB', 'Torfaen',                              'current')
        , ('GB', 'Vale of Glamorgan',                    'current')
        , ('GB', 'Wrexham',                              'current')

        -- ---------------------------------------------------------------------
        -- Scotland: 32 Council Areas (current)
        -- ---------------------------------------------------------------------
        , ('GB', 'Aberdeen City',                        'current')
        , ('GB', 'Aberdeenshire',                        'current')
        , ('GB', 'Angus',                                'current')
        , ('GB', 'Argyll and Bute',                      'current')
        , ('GB', 'City of Edinburgh',                    'current')
        , ('GB', 'Clackmannanshire',                     'current')
        , ('GB', 'Dumfries and Galloway',                'current')
        , ('GB', 'Dundee City',                          'current')
        , ('GB', 'East Ayrshire',                        'current')
        , ('GB', 'East Dunbartonshire',                  'current')
        , ('GB', 'East Lothian',                         'current')
        , ('GB', 'East Renfrewshire',                    'current')
        , ('GB', 'Eilean Siar',                          'current')
        , ('GB', 'Falkirk',                              'current')
        , ('GB', 'Fife',                                 'current')
        , ('GB', 'Glasgow City',                         'current')
        , ('GB', 'Highland',                             'current')
        , ('GB', 'Inverclyde',                           'current')
        , ('GB', 'Midlothian',                           'current')
        , ('GB', 'Moray',                                'current')
        , ('GB', 'North Ayrshire',                       'current')
        , ('GB', 'North Lanarkshire',                    'current')
        , ('GB', 'Orkney Islands',                       'current')
        , ('GB', 'Perth and Kinross',                    'current')
        , ('GB', 'Renfrewshire',                         'current')
        , ('GB', 'Scottish Borders',                     'current')
        , ('GB', 'Shetland Islands',                     'current')
        , ('GB', 'South Ayrshire',                       'current')
        , ('GB', 'South Lanarkshire',                    'current')
        , ('GB', 'Stirling',                             'current')
        , ('GB', 'West Dunbartonshire',                  'current')
        , ('GB', 'West Lothian',                         'current')

        -- ---------------------------------------------------------------------
        -- Northern Ireland: 11 Local Government Districts (current, ONS 2021)
        -- ---------------------------------------------------------------------
        , ('GB', 'Antrim and Newtownabbey',              'current')
        , ('GB', 'Ards and North Down',                  'current')
        , ('GB', 'Armagh City, Banbridge and Craigavon', 'current')
        , ('GB', 'Belfast',                              'current')
        , ('GB', 'Causeway Coast and Glens',             'current')
        , ('GB', 'Derry City and Strabane',              'current')
        , ('GB', 'Fermanagh and Omagh',                  'current')
        , ('GB', 'Lisburn and Castlereagh',              'current')
        , ('GB', 'Mid and East Antrim',                  'current')
        , ('GB', 'Mid Ulster',                           'current')
        , ('GB', 'Newry, Mourne and Down',               'current')

        -- =====================================================================
        -- United Kingdom (GB) - Historic / Abolished Counties
        -- Useful for matching against legacy records
        -- =====================================================================

        -- ---------------------------------------------------------------------
        -- England: Abolished / reorganised counties (historic)
        -- ---------------------------------------------------------------------
        , ('GB', 'Bedfordshire',                         'historic')   -- → Bedford + Central Bedfordshire (2009)
        , ('GB', 'Berkshire',                            'historic')   -- → 6 UAs (1998)
        , ('GB', 'Cheshire',                             'historic')   -- → Cheshire East + Cheshire West and Chester (2009)
        , ('GB', 'Cleveland',                            'historic')   -- → Hartlepool, Middlesbrough, Stockton-on-Tees, Redcar and Cleveland (1996)
        , ('GB', 'Durham',                               'historic')   -- → County Durham UA (2009); short-form alias
        , ('GB', 'Greater London',                       'historic')   -- → 32 boroughs + City of London; still used colloquially
        , ('GB', 'Herefordshire',                        'historic')   -- short-form alias for County of Herefordshire
        , ('GB', 'Northamptonshire',                     'historic')   -- → North + West Northamptonshire (2021)

        -- ---------------------------------------------------------------------
        -- England: Other common aliases / short forms (alias)
        -- ---------------------------------------------------------------------
        , ('GB', 'Bristol',                              'alias')      -- common short form of City of Bristol
        , ('GB', 'Hull',                                 'alias')      -- common short form of City of Kingston upon Hull

        -- ---------------------------------------------------------------------
        -- Wales: Pre-1974 historic counties (historic)
        -- ---------------------------------------------------------------------
        , ('GB', 'Anglesey',                             'historic')   -- → Isle of Anglesey
        , ('GB', 'Breconshire',                          'historic')   -- → Powys
        , ('GB', 'Caernarvonshire',                      'historic')   -- → Gwynedd
        , ('GB', 'Cardiganshire',                        'historic')   -- → Ceredigion
        , ('GB', 'Glamorgan',                            'historic')   -- → Cardiff, Vale of Glamorgan, Bridgend et al.
        , ('GB', 'Merionethshire',                       'historic')   -- → Gwynedd
        , ('GB', 'Montgomeryshire',                      'historic')   -- → Powys
        , ('GB', 'Radnorshire',                          'historic')   -- → Powys

        -- ---------------------------------------------------------------------
        -- Northern Ireland: 6 Traditional Counties (historic)
        -- ---------------------------------------------------------------------
        , ('GB', 'Antrim',                               'historic')
        , ('GB', 'Armagh',                               'historic')
        , ('GB', 'Down',                                 'historic')
        , ('GB', 'Fermanagh',                            'historic')
        , ('GB', 'Londonderry',                          'historic')   -- traditional county name
        , ('GB', 'Derry',                                'alias')      -- common alternative to Londonderry
        , ('GB', 'Derry and Londonderry',                'alias')      -- combined alias used in some legacy systems
        , ('GB', 'Tyrone',                               'historic')

        -- =====================================================================
        -- United States (US): 50 States + District of Columbia (current)
        -- =====================================================================
        , ('US', 'Alabama',                              'current')
        , ('US', 'Alaska',                               'current')
        , ('US', 'Arizona',                              'current')
        , ('US', 'Arkansas',                             'current')
        , ('US', 'California',                           'current')
        , ('US', 'Colorado',                             'current')
        , ('US', 'Connecticut',                          'current')
        , ('US', 'Delaware',                             'current')
        , ('US', 'District of Columbia',                 'current')
        , ('US', 'Florida',                              'current')
        , ('US', 'Georgia',                              'current')
        , ('US', 'Hawaii',                               'current')
        , ('US', 'Idaho',                                'current')
        , ('US', 'Illinois',                             'current')
        , ('US', 'Indiana',                              'current')
        , ('US', 'Iowa',                                 'current')
        , ('US', 'Kansas',                               'current')
        , ('US', 'Kentucky',                             'current')
        , ('US', 'Louisiana',                            'current')
        , ('US', 'Maine',                                'current')
        , ('US', 'Maryland',                             'current')
        , ('US', 'Massachusetts',                        'current')
        , ('US', 'Michigan',                             'current')
        , ('US', 'Minnesota',                            'current')
        , ('US', 'Mississippi',                          'current')
        , ('US', 'Missouri',                             'current')
        , ('US', 'Montana',                              'current')
        , ('US', 'Nebraska',                             'current')
        , ('US', 'Nevada',                               'current')
        , ('US', 'New Hampshire',                        'current')
        , ('US', 'New Jersey',                           'current')
        , ('US', 'New Mexico',                           'current')
        , ('US', 'New York',                             'current')
        , ('US', 'North Carolina',                       'current')
        , ('US', 'North Dakota',                         'current')
        , ('US', 'Ohio',                                 'current')
        , ('US', 'Oklahoma',                             'current')
        , ('US', 'Oregon',                               'current')
        , ('US', 'Pennsylvania',                         'current')
        , ('US', 'Rhode Island',                         'current')
        , ('US', 'South Carolina',                       'current')
        , ('US', 'South Dakota',                         'current')
        , ('US', 'Tennessee',                            'current')
        , ('US', 'Texas',                                'current')
        , ('US', 'Utah',                                 'current')
        , ('US', 'Vermont',                              'current')
        , ('US', 'Virginia',                             'current')
        , ('US', 'Washington',                           'current')
        , ('US', 'West Virginia',                        'current')
        , ('US', 'Wisconsin',                            'current')
        , ('US', 'Wyoming',                              'current')

) AS t(country_code, county_state_name, name_type)
;

get uk city to county mappings
