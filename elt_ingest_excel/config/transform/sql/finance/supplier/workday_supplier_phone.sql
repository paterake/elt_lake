DROP TABLE IF EXISTS workday_supplier_phone
;
CREATE TABLE workday_supplier_phone AS
  WITH cte_supplier_phone
    AS (
SELECT s.supplier_id                         supplier_id
     , s.nrm_vendor_name                     supplier_name
     , s.nrm_country_name                    phone_country
     , s.nrm_country_code                    country_code
     , COALESCE(s.nrm_phone_code, '+44')     international_phone_code
     , s.phone_number_1                      phone_raw
     , 'primary'                             phone_type
     , '_PH1'                                suffix
  FROM src_fin_supplier s
 WHERE NULLIF(UPPER(TRIM(s.phone_number_1)), '') IS NOT NULL
UNION ALL
SELECT s.supplier_id                         supplier_id
     , s.nrm_vendor_name                     supplier_name
     , s.nrm_country_name                    phone_country
     , s.nrm_country_code                    country_code
     , COALESCE(s.nrm_phone_code, '+44')     international_phone_code
     , s.phone_number_2                      phone_raw
     , 'secondary'                           phone_type
     , '_PH2'                                suffix
  FROM src_fin_supplier s
 WHERE NULLIF(UPPER(TRIM(s.phone_number_2)), '') IS NOT NULL
UNION ALL
SELECT s.supplier_id                         supplier_id
     , s.nrm_vendor_name                     supplier_name
     , s.nrm_country_name                    phone_country
     , s.nrm_country_code                    country_code
     , COALESCE(s.nrm_phone_code, '+44')     international_phone_code
     , s.phone_3                             phone_raw
     , 'tertiary'                            phone_type
     , '_PH3'                                suffix
  FROM src_fin_supplier s
 WHERE NULLIF(UPPER(TRIM(s.phone_3)), '') IS NOT NULL
UNION ALL
SELECT s.supplier_id                         supplier_id
     , s.nrm_vendor_name                     supplier_name
     , s.nrm_country_name                    phone_country
     , s.nrm_country_code                    country_code
     , COALESCE(s.nrm_phone_code, '+44')     international_phone_code
     , s.fax_number                          phone_raw
     , 'fax'                                 phone_type
     , '_FAX'                                suffix
  FROM src_fin_supplier s
 WHERE NULLIF(UPPER(TRIM(s.fax_number)), '') IS NOT NULL
       )
     , cte_phone_split
    AS (
SELECT DISTINCT
       p.supplier_id                                                       supplier_id
     , p.supplier_name                                                     supplier_name
     , p.phone_country                                                     phone_country
     , p.country_code                                                      country_code
     , REGEXP_REPLACE(TRIM(p.international_phone_code), '[^0-9]', '', 'g') international_phone_code
     , REGEXP_REPLACE(TRIM(u.phone), '[^0-9]', '', 'g')                    phone_number_raw
     , p.phone_type                                                        phone_type
     , p.suffix                                                            suffix
  FROM cte_supplier_phone p
     , UNNEST(STRING_SPLIT(p.phone_raw, ';')) u(phone)
       )
     , cte_cleaned
    AS (
SELECT s.*
     , CASE
         WHEN REGEXP_REPLACE(s.phone_number_raw, '^0+', '') LIKE s.international_phone_code || '%'
         THEN REGEXP_REPLACE(
                REGEXP_REPLACE(
                  REGEXP_REPLACE(s.phone_number_raw, '^0+', ''),
                  '^' || s.international_phone_code,
                  ''
                ),
                '^0+', ''  -- strip any leading zero from the local number
              )
         ELSE REGEXP_REPLACE(s.phone_number_raw, '^0+', '')
       END                                                                 phone_number
  FROM cte_phone_split s
 WHERE NULLIF(TRIM(s.phone_number_raw), '') IS NOT NULL
       )
    , cte_phone_parse
   AS (
SELECT t.*
     , get_area_code(t.international_phone_code || t.phone_number)         drv_area_code
     , CASE
         WHEN t.phone_type = 'fax'
         THEN 'Fax'
         ELSE get_phone_type(t.international_phone_code || t.phone_number)
       END                                                                 drv_phone_device_type
  FROM cte_cleaned   t
      )
SELECT s.supplier_id                                                       supplier_id
     , s.supplier_name                                                     supplier_name
     , s.supplier_id || s.suffix || '_' || ROW_NUMBER() OVER (
           PARTITION BY s.supplier_id, s.suffix
               ORDER BY s.phone_number_raw
       )                                                                   phone_id
     , s.phone_country                                                     phone_country
     , s.country_code                                                      country_code
     , s.international_phone_code                                          international_phone_code
     , CASE
         WHEN s.drv_phone_device_type = 'Mobile'
         THEN SUBSTR(s.phone_number, 1, 4)
         ELSE s.drv_area_code
       END                                                                 area_code
     , CASE s.drv_phone_device_type
         WHEN 'Mobile'
         THEN SUBSTR(s.phone_number, 5)
         ELSE SUBSTR(s.phone_number, LENGTH(s.drv_area_code) + 1)
       END                                                                 phone_number
     , NULL                                                                phone_number_extension
     , s.drv_phone_device_type                                             phone_device_type
     , 'Yes'                                                               public_flag
     , CASE
         WHEN s.phone_type = 'primary'
         THEN 'Yes'
         ELSE 'No'
       END                                                                 primary_flag
     , NULL                                                                phone_type
     , NULL                                                                use_for
     , NULL                                                                use_for_tenanted
     , NULL                                                                phone_comments
  FROM cte_phone_parse s
;
