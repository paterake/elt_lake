DROP TABLE IF EXISTS workday_supplier_phone
;
CREATE TABLE workday_supplier_phone AS
-- Phone Number 1 (Primary)
SELECT
       TRIM(vendor_id)                                            supplier_id
     , TRIM(vendor_name)                                          supplier_name
     , TRIM(vendor_id) || '_PH1'                                  phone_id
     , TRIM(country)                                              phone_country
     , TRIM(UPPER(country_code))                                  country_code
     , CASE TRIM(UPPER(COALESCE(country_code, 'GB')))
         WHEN 'GB' THEN '+44'
         WHEN 'US' THEN '+1'
         WHEN 'FR' THEN '+33'
         WHEN 'DE' THEN '+49'
         WHEN 'IE' THEN '+353'
         WHEN 'ES' THEN '+34'
         WHEN 'IT' THEN '+39'
         WHEN 'NL' THEN '+31'
         WHEN 'BE' THEN '+32'
         WHEN 'CH' THEN '+41'
         WHEN 'AT' THEN '+43'
         WHEN 'SE' THEN '+46'
         WHEN 'NO' THEN '+47'
         WHEN 'DK' THEN '+45'
         WHEN 'FI' THEN '+358'
         WHEN 'PT' THEN '+351'
         ELSE '+44'
       END                                                        international_phone_code
     , SUBSTRING(REGEXP_REPLACE(phone_number_1, '[^0-9]', ''), 1, 3)
                                                                  area_code
     , SUBSTRING(REGEXP_REPLACE(phone_number_1, '[^0-9]', ''), 4)
                                                                  phone_number
     , NULL                                                       phone_number_extension
     , 'Landline'                                                 phone_device_type
     , TRUE                                                       public_flag
     , TRUE                                                       primary_flag
     , 'Business'                                                 type
     , 'Business'                                                 use_for
     , NULL                                                       use_for_tenanted
     , NULL                                                       comments
  FROM src_fin_supplier
 WHERE phone_number_1 IS NOT NULL
   AND TRIM(phone_number_1) != ''

UNION ALL

-- Phone Number 2
SELECT
       TRIM(vendor_id)                                            supplier_id
     , TRIM(vendor_name)                                          supplier_name
     , TRIM(vendor_id) || '_PH2'                                  phone_id
     , TRIM(country)                                              phone_country
     , TRIM(UPPER(country_code))                                  country_code
     , CASE TRIM(UPPER(COALESCE(country_code, 'GB')))
         WHEN 'GB' THEN '+44'
         WHEN 'US' THEN '+1'
         WHEN 'FR' THEN '+33'
         WHEN 'DE' THEN '+49'
         WHEN 'IE' THEN '+353'
         WHEN 'ES' THEN '+34'
         WHEN 'IT' THEN '+39'
         WHEN 'NL' THEN '+31'
         WHEN 'BE' THEN '+32'
         WHEN 'CH' THEN '+41'
         ELSE '+44'
       END                                                        international_phone_code
     , SUBSTRING(REGEXP_REPLACE(phone_number_2, '[^0-9]', ''), 1, 3)
                                                                  area_code
     , SUBSTRING(REGEXP_REPLACE(phone_number_2, '[^0-9]', ''), 4)
                                                                  phone_number
     , NULL                                                       phone_number_extension
     , 'Landline'                                                 phone_device_type
     , TRUE                                                       public_flag
     , FALSE                                                      primary_flag
     , 'Business'                                                 type
     , 'Business'                                                 use_for
     , NULL                                                       use_for_tenanted
     , NULL                                                       comments
  FROM src_fin_supplier
 WHERE phone_number_2 IS NOT NULL
   AND TRIM(phone_number_2) != ''

UNION ALL

-- Phone 3
SELECT
       TRIM(vendor_id)                                            supplier_id
     , TRIM(vendor_name)                                          supplier_name
     , TRIM(vendor_id) || '_PH3'                                  phone_id
     , TRIM(country)                                              phone_country
     , TRIM(UPPER(country_code))                                  country_code
     , CASE TRIM(UPPER(COALESCE(country_code, 'GB')))
         WHEN 'GB' THEN '+44'
         WHEN 'US' THEN '+1'
         WHEN 'FR' THEN '+33'
         ELSE '+44'
       END                                                        international_phone_code
     , SUBSTRING(REGEXP_REPLACE(phone_3, '[^0-9]', ''), 1, 3)
                                                                  area_code
     , SUBSTRING(REGEXP_REPLACE(phone_3, '[^0-9]', ''), 4)
                                                                  phone_number
     , NULL                                                       phone_number_extension
     , 'Landline'                                                 phone_device_type
     , TRUE                                                       public_flag
     , FALSE                                                      primary_flag
     , 'Business'                                                 type
     , 'Business'                                                 use_for
     , NULL                                                       use_for_tenanted
     , NULL                                                       comments
  FROM src_fin_supplier
 WHERE phone_3 IS NOT NULL
   AND TRIM(phone_3) != ''

UNION ALL

-- Fax Number
SELECT
       TRIM(vendor_id)                                            supplier_id
     , TRIM(vendor_name)                                          supplier_name
     , TRIM(vendor_id) || '_FAX'                                  phone_id
     , TRIM(country)                                              phone_country
     , TRIM(UPPER(country_code))                                  country_code
     , CASE TRIM(UPPER(COALESCE(country_code, 'GB')))
         WHEN 'GB' THEN '+44'
         WHEN 'US' THEN '+1'
         WHEN 'FR' THEN '+33'
         ELSE '+44'
       END                                                        international_phone_code
     , SUBSTRING(REGEXP_REPLACE(fax_number, '[^0-9]', ''), 1, 3)
                                                                  area_code
     , SUBSTRING(REGEXP_REPLACE(fax_number, '[^0-9]', ''), 4)
                                                                  phone_number
     , NULL                                                       phone_number_extension
     , 'Fax'                                                      phone_device_type
     , TRUE                                                       public_flag
     , FALSE                                                      primary_flag
     , 'Business'                                                 type
     , 'Business'                                                 use_for
     , NULL                                                       use_for_tenanted
     , NULL                                                       comments
  FROM src_fin_supplier
 WHERE fax_number IS NOT NULL
   AND TRIM(fax_number) != ''
;
