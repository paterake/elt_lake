DROP TABLE IF EXISTS workday_customer_phone
;
CREATE TABLE workday_customer_phone
    AS
-- Phone Number 1 (Primary)
SELECT
       c.customer_id                                                   customer_id
     , c.customer_id_name                                               customer_name
     , TRIM(c.customer_id) || '_PH1'                                    phone_id
     , TRIM(c.country)                                                  phone_country
     , c.nrm_country_code                                               country_code
     , c.nrm_phone_code                                                 international_phone_code
     , NULL                                                             area_code
     , SUBSTRING(REGEXP_REPLACE(c.phone_1, '[^0-9]', ''), 4)            phone_number
     , NULL                                                             formatted_phone_number
     , NULL                                                             phone_number_extension
     , 'Landline'                                                       phone_device_type
     , 'Yes'                                                            is_public
     , 'Yes'                                                            is_primary
     , 'Business'                                                       phone_type
     , 'Business'                                                       use_for
     , NULL                                                             use_for_tenanted
     , NULL                                                             tenant_formatted_phone
     , NULL                                                             international_formatted_phone
     , NULL                                                             delete_flag
     , NULL                                                             do_not_replace_all
     , NULL                                                             phone_comment
     , TRIM(c.phone_1)                                                  phone
  FROM src_fin_customer                c
 WHERE c.phone_1                       IS NOT NULL
   AND TRIM(c.phone_1)                 != ''

UNION ALL

-- Phone Number 2
SELECT
       TRIM(c.customer_id)                                              customer_id
     , c.customer_id_name                                               customer_name
     , TRIM(c.customer_id) || '_PH2'                                    phone_id
     , TRIM(c.country)                                                  phone_country
     , c.nrm_country_code                                               country_code
     , c.nrm_phone_code                                                 international_phone_code
     , NULL                                                             area_code
     , SUBSTRING(REGEXP_REPLACE(c.phone_2, '[^0-9]', ''), 4)            phone_number
     , NULL                                                             formatted_phone_number
     , NULL                                                             phone_number_extension
     , 'Landline'                                                       phone_device_type
     , 'Yes'                                                            is_public
     , 'No'                                                             is_primary
     , 'Business'                                                       phone_type
     , 'Business'                                                       use_for
     , NULL                                                             use_for_tenanted
     , NULL                                                             tenant_formatted_phone
     , NULL                                                             international_formatted_phone
     , NULL                                                             delete_flag
     , NULL                                                             do_not_replace_all
     , NULL                                                             phone_comment
     , TRIM(c.phone_2)                                                  phone
  FROM src_fin_customer                c
 WHERE c.phone_2                       IS NOT NULL
   AND TRIM(c.phone_2)                 != ''

UNION ALL

-- Phone Number 3
SELECT
       TRIM(c.customer_id)                                              customer_id
     , c.customer_id_name                                               customer_name
     , TRIM(c.customer_id) || '_PH3'                                    phone_id
     , TRIM(c.country)                                                  phone_country
     , c.nrm_country_code                                               country_code
     , c.nrm_phone_code                                                 international_phone_code
     , NULL                                                             area_code
     , SUBSTRING(REGEXP_REPLACE(c.phone_3, '[^0-9]', ''), 4)            phone_number
     , NULL                                                             formatted_phone_number
     , NULL                                                             phone_number_extension
     , 'Landline'                                                       phone_device_type
     , 'Yes'                                                            is_public
     , 'No'                                                             is_primary
     , 'Business'                                                       phone_type
     , 'Business'                                                       use_for
     , NULL                                                             use_for_tenanted
     , NULL                                                             tenant_formatted_phone
     , NULL                                                             international_formatted_phone
     , NULL                                                             delete_flag
     , NULL                                                             do_not_replace_all
     , NULL                                                             phone_comment
     , TRIM(c.phone_3)                                                  phone
  FROM src_fin_customer                c
 WHERE c.phone_3                       IS NOT NULL
   AND TRIM(c.phone_3)                 != ''

UNION ALL

-- Fax Number
SELECT
       TRIM(c.customer_id)                                              customer_id
     , c.customer_id_name                                               customer_name
     , TRIM(c.customer_id) || '_FAX'                                    phone_id
     , TRIM(c.country)                                                  phone_country
     , c.nrm_country_code                                               country_code
     , c.nrm_phone_code                                                 international_phone_code
     , NULL                                                             area_code
     , SUBSTRING(REGEXP_REPLACE(c.fax, '[^0-9]', ''), 4)                phone_number
     , NULL                                                             formatted_phone_number
     , NULL                                                             phone_number_extension
     , 'Fax'                                                            phone_device_type
     , 'Yes'                                                            is_public
     , 'No'                                                             is_primary
     , 'Business'                                                       phone_type
     , 'Business'                                                       use_for
     , NULL                                                             use_for_tenanted
     , NULL                                                             tenant_formatted_phone
     , NULL                                                             international_formatted_phone
     , NULL                                                             delete_flag
     , NULL                                                             do_not_replace_all
     , NULL                                                             phone_comment
     , TRIM(c.fax)                                                      phone
  FROM src_fin_customer                c
 WHERE c.fax                           IS NOT NULL
   AND TRIM(c.fax)                     != ''
;
