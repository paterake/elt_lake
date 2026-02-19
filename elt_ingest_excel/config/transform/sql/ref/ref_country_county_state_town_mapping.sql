DROP TABLE IF EXISTS ref_country_county_state_town_mapping
;
CREATE TABLE ref_country_county_state_town_mapping
    AS
SELECT *
  FROM (VALUES
        -- =====================================================================
        -- England: Metropolitan Counties
        -- =====================================================================
        -- Greater London (London Boroughs)
          ('GB', 'London',                 'London')       -- colloquial city-level entry
        , ('GB', 'Croydon',                'London')
        , ('GB', 'Ilford',                 'London')
        , ('GB', 'Harrow',                 'London')
        , ('GB', 'Wembley',                'London')
        , ('GB', 'Enfield',                'London')
        , ('GB', 'Bromley',                'London')
        , ('GB', 'Romford',                'London')
        , ('GB', 'Ealing',                 'London')
        , ('GB', 'Hackney',                'London')
        , ('GB', 'Islington',              'London')
        , ('GB', 'Hounslow',               'London')
        , ('GB', 'Kingston upon Thames',   'London')
        -- Greater Manchester
        , ('GB', 'Manchester',             'Manchester')
        , ('GB', 'Salford',               'Manchester')
        , ('GB', 'Stockport',             'Manchester')
        , ('GB', 'Bolton',                'Manchester')
        , ('GB', 'Wigan',                 'Manchester')
        , ('GB', 'Oldham',                'Manchester')
        , ('GB', 'Rochdale',              'Manchester')
        , ('GB', 'Bury',                  'Manchester')
        , ('GB', 'Tameside',              'Manchester')
        , ('GB', 'Trafford',              'Manchester')
        -- Merseyside
        , ('GB', 'Liverpool',             'Merseyside')
        , ('GB', 'Birkenhead',            'Merseyside')
        , ('GB', 'Wirral',                'Merseyside')
        , ('GB', 'St Helens',             'Merseyside')
        , ('GB', 'Knowsley',              'Merseyside')
        , ('GB', 'Southport',             'Merseyside')
        -- South Yorkshire
        , ('GB', 'Sheffield',             'South Yorkshire')
        , ('GB', 'Rotherham',             'South Yorkshire')
        , ('GB', 'Doncaster',             'South Yorkshire')
        , ('GB', 'Barnsley',              'South Yorkshire')
        -- Tyne and Wear
        , ('GB', 'Newcastle upon Tyne',   'Tyne and Wear')
        , ('GB', 'Gateshead',             'Tyne and Wear')
        , ('GB', 'Sunderland',            'Tyne and Wear')
        , ('GB', 'South Shields',         'Tyne and Wear')
        , ('GB', 'North Shields',         'Tyne and Wear')
        -- West Midlands
        , ('GB', 'Birmingham',            'West Midlands')
        , ('GB', 'Coventry',              'West Midlands')
        , ('GB', 'Wolverhampton',         'West Midlands')
        , ('GB', 'Walsall',               'West Midlands')
        , ('GB', 'Solihull',              'West Midlands')
        , ('GB', 'Dudley',                'West Midlands')
        , ('GB', 'Sandwell',              'West Midlands')
        -- West Yorkshire
        , ('GB', 'Leeds',                 'West Yorkshire')
        , ('GB', 'Bradford',              'West Yorkshire')
        , ('GB', 'Huddersfield',          'West Yorkshire')
        , ('GB', 'Wakefield',             'West Yorkshire')
        , ('GB', 'Halifax',               'West Yorkshire')
        -- =====================================================================
        -- England: Non-Metropolitan Counties
        -- =====================================================================
        -- Cambridgeshire
        , ('GB', 'Cambridge',             'Cambridgeshire')
        , ('GB', 'Ely',                   'Cambridgeshire')
        -- Cumbria
        , ('GB', 'Carlisle',              'Cumbria')
        , ('GB', 'Barrow-in-Furness',     'Cumbria')
        , ('GB', 'Kendal',                'Cumbria')
        -- Derbyshire
        , ('GB', 'Chesterfield',          'Derbyshire')
        , ('GB', 'Matlock',               'Derbyshire')
        -- Devon
        , ('GB', 'Exeter',                'Devon')
        , ('GB', 'Barnstaple',            'Devon')
        -- Dorset
        , ('GB', 'Dorchester',            'Dorset')
        , ('GB', 'Weymouth',              'Dorset')
        -- East Sussex
        , ('GB', 'Eastbourne',            'East Sussex')
        , ('GB', 'Hastings',              'East Sussex')
        , ('GB', 'Lewes',                 'East Sussex')
        -- Essex
        , ('GB', 'Colchester',            'Essex')
        , ('GB', 'Chelmsford',            'Essex')
        , ('GB', 'Basildon',              'Essex')
        , ('GB', 'Brentwood',             'Essex')
        , ('GB', 'Harlow',                'Essex')
        -- Gloucestershire
        , ('GB', 'Gloucester',            'Gloucestershire')
        , ('GB', 'Cheltenham',            'Gloucestershire')
        , ('GB', 'Stroud',                'Gloucestershire')
        -- Hampshire
        , ('GB', 'Winchester',            'Hampshire')
        , ('GB', 'Basingstoke',           'Hampshire')
        , ('GB', 'Fareham',               'Hampshire')
        , ('GB', 'Gosport',               'Hampshire')
        , ('GB', 'Aldershot',             'Hampshire')
        -- Hertfordshire
        , ('GB', 'St Albans',             'Hertfordshire')
        , ('GB', 'Watford',               'Hertfordshire')
        , ('GB', 'Stevenage',             'Hertfordshire')
        , ('GB', 'Hemel Hempstead',       'Hertfordshire')
        , ('GB', 'Hatfield',              'Hertfordshire')
        -- Kent
        , ('GB', 'Canterbury',            'Kent')
        , ('GB', 'Maidstone',             'Kent')
        , ('GB', 'Dover',                 'Kent')
        , ('GB', 'Ashford',               'Kent')
        , ('GB', 'Tunbridge Wells',        'Kent')
        , ('GB', 'Folkestone',            'Kent')
        , ('GB', 'Margate',               'Kent')
        -- Lancashire
        , ('GB', 'Preston',               'Lancashire')
        , ('GB', 'Lancaster',             'Lancashire')
        , ('GB', 'Burnley',               'Lancashire')
        , ('GB', 'Accrington',            'Lancashire')
        -- Leicestershire
        , ('GB', 'Loughborough',          'Leicestershire')
        , ('GB', 'Hinckley',              'Leicestershire')
        -- Lincolnshire
        , ('GB', 'Lincoln',               'Lincolnshire')
        , ('GB', 'Boston',                'Lincolnshire')
        , ('GB', 'Grantham',              'Lincolnshire')
        -- Norfolk
        , ('GB', 'Norwich',               'Norfolk')
        , ('GB', 'Kings Lynn',            'Norfolk')
        , ('GB', 'Great Yarmouth',        'Norfolk')
        -- North Yorkshire
        , ('GB', 'Harrogate',             'North Yorkshire')
        , ('GB', 'Scarborough',           'North Yorkshire')
        -- Nottinghamshire
        , ('GB', 'Mansfield',             'Nottinghamshire')
        , ('GB', 'Newark',                'Nottinghamshire')
        -- Oxfordshire
        , ('GB', 'Oxford',                'Oxfordshire')
        , ('GB', 'Banbury',               'Oxfordshire')
        -- Somerset
        , ('GB', 'Taunton',               'Somerset')
        , ('GB', 'Bridgwater',            'Somerset')
        , ('GB', 'Yeovil',                'Somerset')
        -- Staffordshire
        , ('GB', 'Stafford',              'Staffordshire')
        , ('GB', 'Lichfield',             'Staffordshire')
        , ('GB', 'Tamworth',              'Staffordshire')
        , ('GB', 'Burton upon Trent',     'Staffordshire')
        -- Suffolk
        , ('GB', 'Ipswich',               'Suffolk')
        , ('GB', 'Bury St Edmunds',       'Suffolk')
        , ('GB', 'Lowestoft',             'Suffolk')
        -- Surrey
        , ('GB', 'Guildford',             'Surrey')
        , ('GB', 'Woking',                'Surrey')
        , ('GB', 'Reigate',               'Surrey')
        , ('GB', 'Epsom',                 'Surrey')
        -- Warwickshire
        , ('GB', 'Warwick',               'Warwickshire')
        , ('GB', 'Leamington Spa',        'Warwickshire')
        , ('GB', 'Nuneaton',              'Warwickshire')
        , ('GB', 'Rugby',                 'Warwickshire')
        -- West Sussex
        , ('GB', 'Worthing',              'West Sussex')
        , ('GB', 'Chichester',            'West Sussex')
        , ('GB', 'Crawley',               'West Sussex')
        , ('GB', 'Horsham',               'West Sussex')
        -- Worcestershire
        , ('GB', 'Worcester',             'Worcestershire')
        , ('GB', 'Kidderminster',         'Worcestershire')
        , ('GB', 'Redditch',              'Worcestershire')
        -- =====================================================================
        -- England: Unitary Authorities (outside London)
        -- =====================================================================
        -- Bath and North East Somerset
        , ('GB', 'Bath',                  'Bath and North East Somerset')
        -- Bedford
        , ('GB', 'Bedford',               'Bedfordshire')
        -- Blackburn with Darwen
        , ('GB', 'Blackburn',             'Blackburn with Darwen')
        -- Blackpool
        , ('GB', 'Blackpool',             'Blackpool')
        -- Bournemouth, Christchurch and Poole
        , ('GB', 'Bournemouth',           'Bournemouth')
        , ('GB', 'Poole',                 'Poole')
        , ('GB', 'Christchurch',          'Dorset')
        -- Bracknell Forest
        , ('GB', 'Bracknell',             'Bracknell Forest')
        -- Brighton and Hove
        , ('GB', 'Brighton',              'Brighton and Hove')
        , ('GB', 'Hove',                  'Brighton and Hove')
        -- Buckinghamshire (UA since 2020)
        , ('GB', 'Aylesbury',             'Buckinghamshire')
        , ('GB', 'High Wycombe',          'Buckinghamshire')
        -- Central Bedfordshire
        , ('GB', 'Dunstable',             'Bedfordshire')
        , ('GB', 'Leighton Buzzard',      'Bedfordshire')
        -- Cheshire East
        , ('GB', 'Crewe',                 'Cheshire')
        , ('GB', 'Macclesfield',          'Cheshire')
        , ('GB', 'Congleton',             'Cheshire')
        -- Cheshire West and Chester
        , ('GB', 'Chester',               'Cheshire')
        , ('GB', 'Ellesmere Port',        'Cheshire')
        -- City of Bristol
        , ('GB', 'Bristol',               'Bristol, City of')
        -- City of Kingston upon Hull
        , ('GB', 'Hull',                  'Kingston upon Hull, City of')
        , ('GB', 'Kingston upon Hull',    'Kingston upon Hull, City of')
        -- Cornwall
        , ('GB', 'Truro',                 'Cornwall')
        , ('GB', 'Penzance',              'Cornwall')
        , ('GB', 'St Ives',               'Cornwall')
        , ('GB', 'Newquay',               'Cornwall')
        , ('GB', 'Falmouth',              'Cornwall')
        -- Durham
        , ('GB', 'Durham',                'Durham')
        -- Herefordshire
        , ('GB', 'Hereford',              'Herefordshire')
        -- Darlington
        , ('GB', 'Darlington',            'Darlington')
        -- Derby
        , ('GB', 'Derby',                 'Derby')
        -- East Riding of Yorkshire
        , ('GB', 'Beverley',              'East Riding of Yorkshire')
        , ('GB', 'Bridlington',           'East Riding of Yorkshire')
        , ('GB', 'Goole',                 'East Riding of Yorkshire')
        -- Halton
        , ('GB', 'Runcorn',               'Halton')
        , ('GB', 'Widnes',                'Halton')
        -- Hartlepool
        , ('GB', 'Hartlepool',            'Hartlepool')
        -- Isle of Wight
      --, ('GB', 'Newport',               'Isle of Wight')          -- NB: different Newport to Wales
        , ('GB', 'Ryde',                  'Isle of Wight')
        -- Leicester
        , ('GB', 'Leicester',             'Leicester')
        -- Luton
        , ('GB', 'Luton',                 'Luton')
        -- Medway
        , ('GB', 'Rochester',             'Medway')
        , ('GB', 'Chatham',               'Medway')
        , ('GB', 'Gillingham',            'Medway')
        -- Middlesbrough
        , ('GB', 'Middlesbrough',         'Middlesbrough')
        -- Milton Keynes
        , ('GB', 'Milton Keynes',         'Milton Keynes')
        -- North East Lincolnshire
        , ('GB', 'Grimsby',               'North East Lincolnshire')
        , ('GB', 'Cleethorpes',           'North East Lincolnshire')
        -- North Lincolnshire
        , ('GB', 'Scunthorpe',            'North Lincolnshire')
        -- North Northamptonshire
        , ('GB', 'Corby',                 'Northamptonshire')
        , ('GB', 'Kettering',             'Northamptonshire')
        , ('GB', 'Wellingborough',        'Northamptonshire')
        -- North Somerset
        , ('GB', 'Weston-super-Mare',     'North Somerset')
        -- Northumberland
        , ('GB', 'Northumberland',        'Northumberland')
        , ('GB', 'Alnwick',               'Northumberland')
        , ('GB', 'Hexham',                'Northumberland')
        -- Nottingham
        , ('GB', 'Nottingham',            'Nottingham')
        -- Peterborough
        , ('GB', 'Peterborough',          'Peterborough')
        -- Plymouth
        , ('GB', 'Plymouth',              'Plymouth')
        -- Portsmouth
        , ('GB', 'Portsmouth',            'Portsmouth')
        -- Reading
        , ('GB', 'Reading',               'Reading')
        -- Redcar and Cleveland
        , ('GB', 'Redcar',                'Redcar and Cleveland')
        -- Rutland
        , ('GB', 'Oakham',                'Rutland')
        -- Shropshire
        , ('GB', 'Shrewsbury',            'Shropshire')
        , ('GB', 'Oswestry',              'Shropshire')
        -- Slough
        , ('GB', 'Slough',                'Slough')
        -- South Gloucestershire
        , ('GB', 'Thornbury',             'South Gloucestershire')
        , ('GB', 'Yate',                  'South Gloucestershire')
        -- Southampton
        , ('GB', 'Southampton',           'Southampton')
        -- Southend-on-Sea
        , ('GB', 'Southend-on-Sea',       'Southend-on-Sea')
        -- Stockton-on-Tees
        , ('GB', 'Stockton-on-Tees',      'Stockton-on-Tees')
        -- Stoke-on-Trent
        , ('GB', 'Stoke-on-Trent',        'Stoke-on-Trent')
        , ('GB', 'Hanley',                'Stoke-on-Trent')
        -- Swindon
        , ('GB', 'Swindon',               'Swindon')
        -- Telford and Wrekin
        , ('GB', 'Telford',               'Telford and Wrekin')
        -- Thurrock
        , ('GB', 'Grays',                 'Thurrock')
        , ('GB', 'Tilbury',               'Thurrock')
        -- Torbay
        , ('GB', 'Torquay',               'Torbay')
        , ('GB', 'Paignton',              'Torbay')
        -- Warrington
        , ('GB', 'Warrington',            'Warrington')
        -- West Berkshire
        , ('GB', 'Newbury',               'West Berkshire')
        -- West Northamptonshire
        , ('GB', 'Northampton',           'Northamptonshire')
        , ('GB', 'Daventry',              'Northamptonshire')
        -- Wiltshire
        , ('GB', 'Salisbury',             'Wiltshire')
        , ('GB', 'Trowbridge',            'Wiltshire')
        , ('GB', 'Chippenham',            'Wiltshire')
        -- Windsor and Maidenhead
        , ('GB', 'Windsor',               'Windsor and Maidenhead')
        , ('GB', 'Maidenhead',            'Windsor and Maidenhead')
        -- Wokingham
        , ('GB', 'Wokingham',             'Wokingham')
        , ('GB', 'Woodley',               'Wokingham')
        -- York
        , ('GB', 'York',                  'York')
        -- =====================================================================
        -- Wales: 22 Principal Areas
        -- =====================================================================
        , ('GB', 'Cardiff',               'Cardiff')
        , ('GB', 'Swansea',               'Swansea')
        , ('GB', 'Newport',               'Newport')
        , ('GB', 'Barry',                 'Vale of Glamorgan')
        , ('GB', 'Penarth',               'Vale of Glamorgan')
        , ('GB', 'Bridgend',              'Bridgend')
        , ('GB', 'Pontypridd',            'Rhondda Cynon Taff')
        , ('GB', 'Merthyr Tydfil',        'Merthyr Tydfil')
        , ('GB', 'Caerphilly',            'Caerphilly')
        , ('GB', 'Abertillery',           'Blaenau Gwent')
        , ('GB', 'Ebbw Vale',             'Blaenau Gwent')
        , ('GB', 'Pontypool',             'Torfaen')
        , ('GB', 'Monmouth',              'Monmouthshire')
        , ('GB', 'Neath',                 'Neath Port Talbot')
        , ('GB', 'Port Talbot',           'Neath Port Talbot')
        , ('GB', 'Wrexham',               'Wrexham')
        , ('GB', 'Rhyl',                  'Denbighshire')
        , ('GB', 'Colwyn Bay',            'Conwy')
        , ('GB', 'Llandudno',             'Conwy')
        , ('GB', 'Flint',                 'Flintshire')
        , ('GB', 'Bangor',                'Gwynedd')
        , ('GB', 'Aberystwyth',           'Ceredigion')
        , ('GB', 'Carmarthen',            'Carmarthenshire')
        , ('GB', 'Llanelli',              'Carmarthenshire')
        , ('GB', 'Pembroke',              'Pembrokeshire')
        , ('GB', 'Haverfordwest',         'Pembrokeshire')
        , ('GB', 'Welshpool',             'Powys')
        , ('GB', 'Newtown',               'Powys')
        , ('GB', 'Holyhead',              'Isle of Anglesey')
        -- =====================================================================
        -- Scotland: Council Areas
        -- =====================================================================
        , ('GB', 'Edinburgh',             'Edinburgh, City of')
        , ('GB', 'Glasgow',               'Glasgow City')
        , ('GB', 'Aberdeen',              'Aberdeen City')
        , ('GB', 'Dundee',                'Dundee City')
        , ('GB', 'Inverness',             'Highland')
        , ('GB', 'Perth',                 'Perth and Kinross')
        , ('GB', 'Stirling',              'Stirling')
        , ('GB', 'Falkirk',               'Falkirk')
        , ('GB', 'Paisley',               'Renfrewshire')
        , ('GB', 'East Kilbride',         'South Lanarkshire')
        , ('GB', 'Hamilton',              'South Lanarkshire')
        , ('GB', 'Motherwell',            'North Lanarkshire')
        , ('GB', 'Coatbridge',            'North Lanarkshire')
        , ('GB', 'Dumfries',              'Dumfries and Galloway')
        , ('GB', 'Kilmarnock',            'East Ayrshire')
        , ('GB', 'Ayr',                   'South Ayrshire')
        , ('GB', 'Greenock',              'Inverclyde')
        , ('GB', 'Livingston',            'West Lothian')
        , ('GB', 'Kirkcaldy',             'Fife')
        , ('GB', 'Dunfermline',           'Fife')
        , ('GB', 'Elgin',                 'Moray')
        , ('GB', 'Fort William',          'Highland')
        -- =====================================================================
        -- Northern Ireland: Old District Councils (Workday values; pre-2015 reorganisation)
        -- =====================================================================
        , ('GB', 'Belfast',               'Belfast')
        , ('GB', 'Derry',                 'Derry')
        , ('GB', 'Londonderry',           'Derry')
        , ('GB', 'Lisburn',               'Lisburn')
        , ('GB', 'Newry',                 'Newry and Mourne')
        , ('GB', 'Armagh',                'County Armagh')
        , ('GB', 'Banbridge',             'Banbridge')
        , ('GB', 'Antrim',                'County Antrim')
        , ('GB', 'Newtownabbey',          'Newtownabbey')
        , ('GB', 'Ballymena',             'Ballymena')
        , ('GB', 'Carrickfergus',         'Carrickfergus')
        , ('GB', 'Enniskillen',           'County Fermanagh')
        , ('GB', 'Omagh',                 'Omagh')
        , ('GB', 'Cookstown',             'Cookstown')
        , ('GB', 'Magherafelt',           'Magherafelt')
        , ('GB', 'Coleraine',             'Coleraine')
        , ('GB', 'Ballymoney',            'Ballymoney')
      --, ('GB', 'Bangor',                'Ards')
        , ('GB', 'Newtownards',           'Ards')
        , ('GB', 'Castlereagh',           'Castlereagh')
) AS t(country_code, town_city_name, county_state_name)
;
