DROP TABLE IF EXISTS ref_supplier_country_code_mapping
;
-- Maps dirty source country codes to canonical country_code
CREATE TABLE ref_supplier_country_code_mapping
    AS
SELECT * FROM (VALUES
    ('AR',   'AR'),
    ('AU',   'AU'),
    ('BE',   'BE'),
    ('CA',   'CA'),
    ('CH',   'CH'),
    ('DE',   'DE'),
    ('DK',   'DK'),
    ('ES',   'ES'),
    ('FR',   'FR'),
    ('GB',   'GB'),
    ('IE',   'IE'),
    ('LV',   'LV'),
    ('NL',   'NL'),
    ('NZ',   'NZ'),
    ('PL',   'PL'),
    ('SZ',   'CH'),  -- incorrect code for Switzerland corrected
    ('US',   'US')

) AS t(source_country_code, country_code)
;
