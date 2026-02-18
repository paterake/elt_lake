DROP TABLE IF EXISTS ref_source_supplier_payment_terms
;
CREATE TABLE ref_source_supplier_payment_terms
    AS
SELECT
       *
  FROM (VALUES
          ('DUE IMMEDIATELY' , 'Immediate')
        , ('IMMEDIATE'       , 'Immediate')
        , ('30 EOM'          , 'Net 30')
        , ('14 DAYS'         , 'Net 30')
        , ('15 DAYS'         , 'Net 30')
        , ('30 DAYS'         , 'Net 30')
        , ('7 DAYS'          , 'Net 30')
        , ('21 DAYS'         , 'Net 30')
        , ('15TH MONTH'      , 'Net 30')
        , ('NET 10'          , 'Net 10')
        , ('NET 30'          , 'Net 30')
        , ('2% 10, NET 30'   , '2% 10, Net 30')
       ) AS t(source_payment_terms, workday_payment_terms)
;
