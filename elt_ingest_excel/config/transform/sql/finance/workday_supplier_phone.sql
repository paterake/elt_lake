DROP TABLE IF EXISTS workday_supplier_phone
;
CREATE TABLE workday_supplier_phone 
    AS
  WITH cte_country_phone_code 
    AS (
SELECT 'GB' country_code, '+44'  phone_code UNION ALL
SELECT 'US',              '+1'              UNION ALL
SELECT 'CA',              '+1'              UNION ALL
SELECT 'FR',              '+33'             UNION ALL
SELECT 'DE',              '+49'             UNION ALL
SELECT 'IE',              '+353'            UNION ALL
SELECT 'ES',              '+34'             UNION ALL
SELECT 'IT',              '+39'             UNION ALL
SELECT 'NL',              '+31'             UNION ALL
SELECT 'BE',              '+32'             UNION ALL
SELECT 'CH',              '+41'             UNION ALL
SELECT 'AT',              '+43'             UNION ALL
SELECT 'SE',              '+46'             UNION ALL
SELECT 'NO',              '+47'             UNION ALL
SELECT 'DK',              '+45'             UNION ALL
SELECT 'FI',              '+358'            UNION ALL
SELECT 'PT',              '+351'            UNION ALL
SELECT 'PL',              '+48'             UNION ALL
SELECT 'GR',              '+30'             UNION ALL
SELECT 'CZ',              '+420'            UNION ALL
SELECT 'HU',              '+36'             UNION ALL
SELECT 'RO',              '+40'             UNION ALL
SELECT 'AU',              '+61'             UNION ALL
SELECT 'NZ',              '+64'             UNION ALL
SELECT 'JP',              '+81'             UNION ALL
SELECT 'CN',              '+86'             UNION ALL
SELECT 'IN',              '+91'             UNION ALL
SELECT 'SG',              '+65'             UNION ALL
SELECT 'HK',              '+852'            UNION ALL
SELECT 'AE',              '+971'            UNION ALL
SELECT 'ZA',              '+27'             UNION ALL
SELECT 'BR',              '+55'             UNION ALL
SELECT 'MX',              '+52'
       )
-- Phone Number 1 (Primary)
SELECT
       TRIM(s.supplier_id)                                           supplier_id
     , TRIM(s.vendor_name)                                           supplier_name
     , TRIM(s.supplier_id) || '_PH1'                                 phone_id
     , TRIM(s.country)                                               phone_country
     , TRIM(UPPER(s.country_code))                                   country_code
     , COALESCE(p.phone_code, '+44')                                 international_phone_code
     , NULL                                                          area_code
     , SUBSTRING(REGEXP_REPLACE(s.phone_number_1, '[^0-9]', ''), 4)  phone_number
     , NULL                                                          phone_number_extension
     , 'Landline'                                                    phone_device_type
     , 'Yes'                                                         public_flag
     , 'Yes'                                                         primary_flag
     , 'Business'                                                    phone_type
     , 'Business'                                                    use_for
     , NULL                                                          use_for_tenanted
     , NULL                                                          phone_comments
  FROM src_fin_supplier                s
       LEFT OUTER JOIN 
       cte_country_phone_code          p
          ON p.country_code            = TRIM(UPPER(COALESCE(s.country_code, 'GB')))
 WHERE s.phone_number_1                IS NOT NULL
   AND TRIM(s.phone_number_1)          != ''

UNION ALL

-- Phone Number 2
SELECT
       TRIM(s.supplier_id)                                           supplier_id
     , TRIM(s.vendor_name)                                           supplier_name
     , TRIM(s.supplier_id) || '_PH1'                                 phone_id
     , TRIM(s.country)                                               phone_country
     , TRIM(UPPER(s.country_code))                                   country_code
     , COALESCE(p.phone_code, '+44')                                 international_phone_code
     , NULL                                                          area_code
     , SUBSTRING(REGEXP_REPLACE(s.phone_number_2, '[^0-9]', ''), 4)  phone_number
     , NULL                                                          phone_number_extension
     , 'Landline'                                                    phone_device_type
     , 'Yes'                                                         public_flag
     , 'Yes'                                                         primary_flag
     , 'Business'                                                    phone_type
     , 'Business'                                                    use_for
     , NULL                                                          use_for_tenanted
     , NULL                                                          phone_comments
  FROM src_fin_supplier                s
       LEFT OUTER JOIN 
       cte_country_phone_code          p
          ON p.country_code            = TRIM(UPPER(COALESCE(s.country_code, 'GB')))
 WHERE s.phone_number_2                IS NOT NULL
   AND TRIM(s.phone_number_2)          != ''

UNION ALL

-- Phone 3
SELECT
       TRIM(s.supplier_id)                                           supplier_id
     , TRIM(s.vendor_name)                                           supplier_name
     , TRIM(s.supplier_id) || '_PH1'                                 phone_id
     , TRIM(s.country)                                               phone_country
     , TRIM(UPPER(s.country_code))                                   country_code
     , COALESCE(p.phone_code, '+44')                                 international_phone_code
     , NULL                                                          area_code
     , SUBSTRING(REGEXP_REPLACE(s.phone_3, '[^0-9]', ''), 4)         phone_number
     , NULL                                                          phone_number_extension
     , 'Landline'                                                    phone_device_type
     , 'Yes'                                                         public_flag
     , 'Yes'                                                         primary_flag
     , 'Business'                                                    phone_type
     , 'Business'                                                    use_for
     , NULL                                                          use_for_tenanted
     , NULL                                                          phone_comments
  FROM src_fin_supplier                s
       LEFT OUTER JOIN 
       cte_country_phone_code          p
          ON p.country_code            = TRIM(UPPER(COALESCE(s.country_code, 'GB')))
 WHERE s.phone_3                       IS NOT NULL
   AND TRIM(s.phone_3)                 != ''

UNION ALL

-- Fax Number
SELECT
       TRIM(s.supplier_id)                                           supplier_id
     , TRIM(s.vendor_name)                                           supplier_name
     , TRIM(s.supplier_id) || '_PH1'                                 phone_id
     , TRIM(s.country)                                               phone_country
     , TRIM(UPPER(s.country_code))                                   country_code
     , COALESCE(p.phone_code, '+44')                                 international_phone_code
     , NULL                                                          area_code
     , SUBSTRING(REGEXP_REPLACE(s.fax_number, '[^0-9]', ''), 4)      phone_number
     , NULL                                                          phone_number_extension
     , 'Fax'                                                         phone_device_type
     , 'Yes'                                                         public_flag
     , 'Yes'                                                         primary_flag
     , 'Business'                                                    phone_type
     , 'Business'                                                    use_for
     , NULL                                                          use_for_tenanted
     , NULL                                                          phone_comments
  FROM src_fin_supplier                s
       LEFT OUTER JOIN 
       cte_country_phone_code          p
          ON p.country_code            = TRIM(UPPER(COALESCE(s.country_code, 'GB')))
 WHERE s.fax_number                    IS NOT NULL
   AND TRIM(s.fax_number)              != ''
