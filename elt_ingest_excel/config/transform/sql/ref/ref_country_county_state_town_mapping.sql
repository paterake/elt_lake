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
          ('GB', 'London',                 'Greater London')       -- colloquial city-level entry
        , ('GB', 'Croydon',                'Greater London')
        , ('GB', 'Ilford',                 'Greater London')
        , ('GB', 'Harrow',                 'Greater London')
        , ('GB', 'Wembley',                'Greater London')
        , ('GB', 'Enfield',                'Greater London')
        , ('GB', 'Bromley',                'Greater London')
        , ('GB', 'Romford',                'Greater London')
        , ('GB', 'Ealing',                 'Greater London')
        , ('GB', 'Hackney',                'Greater London')
        , ('GB', 'Islington',              'Greater London')
        , ('GB', 'Hounslow',               'Greater London')
        , ('GB', 'Kingston upon Thames',   'Greater London')
        -- Greater Manchester
        , ('GB', 'Manchester',             'Greater Manchester')
        , ('GB', 'Salford',               'Greater Manchester')
        , ('GB', 'Stockport',             'Greater Manchester')
        , ('GB', 'Bolton',                'Greater Manchester')
        , ('GB', 'Wigan',                 'Greater Manchester')
        , ('GB', 'Oldham',                'Greater Manchester')
        , ('GB', 'Rochdale',              'Greater Manchester')
        , ('GB', 'Bury',                  'Greater Manchester')
        , ('GB', 'Tameside',              'Greater Manchester')
        , ('GB', 'Trafford',              'Greater Manchester')
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
        , ('GB', 'Bedford',               'Bedford')
        -- Blackburn with Darwen
        , ('GB', 'Blackburn',             'Blackburn with Darwen')
        -- Blackpool
        , ('GB', 'Blackpool',             'Blackpool')
        -- Bournemouth, Christchurch and Poole
        , ('GB', 'Bournemouth',           'Bournemouth, Christchurch and Poole')
        , ('GB', 'Poole',                 'Bournemouth, Christchurch and Poole')
        , ('GB', 'Christchurch',          'Bournemouth, Christchurch and Poole')
        -- Bracknell Forest
        , ('GB', 'Bracknell',             'Bracknell Forest')
        -- Brighton and Hove
        , ('GB', 'Brighton',              'Brighton and Hove')
        , ('GB', 'Hove',                  'Brighton and Hove')
        -- Buckinghamshire (UA since 2020)
        , ('GB', 'Aylesbury',             'Buckinghamshire')
        , ('GB', 'High Wycombe',          'Buckinghamshire')
        -- Central Bedfordshire
        , ('GB', 'Dunstable',             'Central Bedfordshire')
        , ('GB', 'Leighton Buzzard',      'Central Bedfordshire')
        -- Cheshire East
        , ('GB', 'Crewe',                 'Cheshire East')
        , ('GB', 'Macclesfield',          'Cheshire East')
        , ('GB', 'Congleton',             'Cheshire East')
        -- Cheshire West and Chester
        , ('GB', 'Chester',               'Cheshire West and Chester')
        , ('GB', 'Ellesmere Port',        'Cheshire West and Chester')
        -- City of Bristol
        , ('GB', 'Bristol',               'City of Bristol')
        -- City of Kingston upon Hull
        , ('GB', 'Hull',                  'City of Kingston upon Hull')
        , ('GB', 'Kingston upon Hull',    'City of Kingston upon Hull')
        -- Cornwall
        , ('GB', 'Truro',                 'Cornwall')
        , ('GB', 'Penzance',              'Cornwall')
        , ('GB', 'St Ives',               'Cornwall')
        , ('GB', 'Newquay',               'Cornwall')
        , ('GB', 'Falmouth',              'Cornwall')
        -- County Durham
        , ('GB', 'Durham',                'County Durham')
        -- County of Herefordshire
        , ('GB', 'Hereford',              'County of Herefordshire')
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
        , ('GB', 'Corby',                 'North Northamptonshire')
        , ('GB', 'Kettering',             'North Northamptonshire')
        , ('GB', 'Wellingborough',        'North Northamptonshire')
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
        , ('GB', 'Northampton',           'West Northamptonshire')
        , ('GB', 'Daventry',              'West Northamptonshire')
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
        , ('GB', 'Pontypridd',            'Rhondda Cynon Taf')
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
        , ('GB', 'Edinburgh',             'City of Edinburgh')
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
        -- Northern Ireland: 11 Local Government Districts (ONS 2021)
        -- =====================================================================
        , ('GB', 'Belfast',               'Belfast')
        , ('GB', 'Derry',                 'Derry City and Strabane')
        , ('GB', 'Londonderry',           'Derry City and Strabane')
        , ('GB', 'Lisburn',               'Lisburn and Castlereagh')
        , ('GB', 'Newry',                 'Newry, Mourne and Down')
        , ('GB', 'Armagh',                'Armagh City, Banbridge and Craigavon')
        , ('GB', 'Banbridge',             'Armagh City, Banbridge and Craigavon')
        , ('GB', 'Antrim',                'Antrim and Newtownabbey')
        , ('GB', 'Newtownabbey',          'Antrim and Newtownabbey')
        , ('GB', 'Ballymena',             'Mid and East Antrim')
        , ('GB', 'Carrickfergus',         'Mid and East Antrim')
        , ('GB', 'Enniskillen',           'Fermanagh and Omagh')
        , ('GB', 'Omagh',                 'Fermanagh and Omagh')
        , ('GB', 'Cookstown',             'Mid Ulster')
        , ('GB', 'Magherafelt',           'Mid Ulster')
        , ('GB', 'Coleraine',             'Causeway Coast and Glens')
        , ('GB', 'Ballymoney',            'Causeway Coast and Glens')
      --, ('GB', 'Bangor',                'Ards and North Down')
        , ('GB', 'Newtownards',           'Ards and North Down')
        , ('GB', 'Castlereagh',           'Lisburn and Castlereagh')
) AS t(country_code, town_city_name, county_state_name)
;
