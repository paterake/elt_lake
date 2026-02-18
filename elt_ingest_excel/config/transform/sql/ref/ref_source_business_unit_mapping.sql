DROP TABLE IF EXISTS ref_source_business_unit_mapping
;
CREATE TABLE ref_source_business_unit_mapping
    AS
SELECT
       *
  FROM (VALUES
         ('NFC' , 'National Football Centre Limited')
       , ('FA'  , 'The Football Association')
       , ('WNSL', 'Wembley National Stadium Ltd')
) AS t(source_value, target_value)
;
