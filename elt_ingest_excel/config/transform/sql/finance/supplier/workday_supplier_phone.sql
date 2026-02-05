DROP TABLE IF EXISTS workday_supplier_phone
;
CREATE TABLE workday_supplier_phone
    AS
-- Phone Number 1 (Primary)
SELECT
       s.supplier_id                                                 supplier_id
     , s.nrm_vendor_name                                             supplier_name
     , s.supplier_id || '_PH1'                                       phone_id
     , s.nrm_country_name                                            phone_country
     , s.nrm_country_code                                            country_code
     , COALESCE(s.nrm_phone_code, '+44')                             international_phone_code
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
 WHERE s.phone_number_1                IS NOT NULL
   AND TRIM(s.phone_number_1)          != ''

UNION ALL

-- Phone Number 2
SELECT
       s.supplier_id                                                 supplier_id
     , s.nrm_vendor_name                                             supplier_name
     , s.supplier_id || '_PH1'                                       phone_id
     , s.nrm_country_name                                            phone_country
     , s.nrm_country_code                                            country_code
     , COALESCE(s.nrm_phone_code, '+44')                             international_phone_code
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
 WHERE s.phone_number_2                IS NOT NULL
   AND TRIM(s.phone_number_2)          != ''

UNION ALL

-- Phone 3
SELECT
       s.supplier_id                                                 supplier_id
     , s.nrm_vendor_name                                             supplier_name
     , s.supplier_id || '_PH1'                                       phone_id
     , s.nrm_country_name                                            phone_country
     , s.nrm_country_code                                            country_code
     , COALESCE(s.nrm_phone_code, '+44')                             international_phone_code
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
 WHERE s.phone_3                       IS NOT NULL
   AND TRIM(s.phone_3)                 != ''

UNION ALL

-- Fax Number
SELECT
       s.supplier_id                                                 supplier_id
     , s.nrm_vendor_name                                             supplier_name
     , s.supplier_id || '_PH1'                                       phone_id
     , s.nrm_country_name                                            phone_country
     , s.nrm_country_code                                            country_code
     , COALESCE(s.nrm_phone_code, '+44')                             international_phone_code
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
 WHERE s.fax_number                    IS NOT NULL
   AND TRIM(s.fax_number)              != ''
;
