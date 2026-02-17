DROP TABLE IF EXISTS ref_supplier_category_mapping
;
-- Maps dirty source supplier categories (from vendor_class_id)
-- to canonical Workday supplier categories (valid values)
-- Valid targets:
-- - Information Technology
-- - Office Supplies
-- - Professional Services
-- - Property Managers
-- - Services
-- - Utilities
CREATE TABLE ref_supplier_category_mapping
    AS
SELECT * FROM (VALUES
      ('INFORMATION TECHNOLOGY' , 'Information Technology')
    , ('OFFICE SUPPLIES'        , 'Office Supplies')
    , ('PROFESSIONAL SERVICES'  , 'Professional Services')
    , ('PROPERTY MANAGERS'      , 'Property Managers')
    , ('SERVICES'               , 'Services')
    , ('UTILITIES'              , 'Utilities')
    -- Source → Target mappings from provided list
    , ('MENS CLUBS'             , 'Services')
    , ('EUROS'                  , 'Services')
    , ('REFS INAC'              , 'Professional Services')
    , ('QAR'                    , 'Services')
    , ('GENERAL'                , 'Services')
    , ('REFS CMH'               , 'Professional Services')
    , ('AU DOLLARS'             , 'Services')
    , ('DAN KRONER'             , 'Services')
    , ('WOMENS'                 , 'Services')
    , ('CW'                     , 'Services')
    , ('CHARITY'                , 'Services')
    , ('LEAGUE'                 , 'Services')
    , ('NOR KRONE'              , 'Services')
    , ('SEK'                    , 'Services')
    , ('GBPFOREIGN'             , 'Services')
    , ('PLN'                    , 'Services')
    , ('NIKE PARTN'             , 'Services')
    , ('GFSP'                   , 'Services')
    , ('COUNTY FAS'             , 'Services')
    , ('AED'                    , 'Services')
    , ('US DOLLARS'             , 'Services')
    , ('IR35'                   , 'Professional Services')
    , ('ONE OFF'                , 'Services')
    , ('PM&H'                   , 'Professional Services')
    , ('CHF'                    , 'Services')
    , ('DD'                     , 'Services')
) AS t(source_supplier_category, supplier_category)
;
