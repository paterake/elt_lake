DROP TABLE IF EXISTS workday_customer_phone
;
CREATE TABLE workday_customer_phone AS
  WITH cte_customer_phone
    AS (
SELECT c.customer_id                         customer_id
     , c.nrm_customer_name                   customer_name
     , TRIM(c.country)                       phone_country
     , c.nrm_country_code                    country_code
     , c.nrm_phone_code                      international_phone_code
     , c.phone_1                             phone_raw
     , 'primary'                             phone_type
     , '_PH1'                                suffix
  FROM src_fin_customer                      c
 WHERE NULLIF(UPPER(TRIM(c.phone_1)), '') IS NOT NULL
UNION ALL
SELECT c.customer_id                         customer_id
     , c.nrm_customer_name                   customer_name
     , TRIM(c.country)                       phone_country
     , c.nrm_country_code                    country_code
     , c.nrm_phone_code                      international_phone_code
     , c.phone_2                             phone_raw
     , 'secondary'                           phone_type
     , '_PH2'                                suffix
  FROM src_fin_customer                      c
 WHERE NULLIF(UPPER(TRIM(c.phone_2)), '') IS NOT NULL
UNION ALL
SELECT c.customer_id                         customer_id
     , c.nrm_customer_name                   customer_name
     , TRIM(c.country)                       phone_country
     , c.nrm_country_code                    country_code
     , c.nrm_phone_code                      international_phone_code
     , c.phone_3                             phone_raw
     , 'tertiary'                            phone_type
     , '_PH3'                                suffix
  FROM src_fin_customer                      c
 WHERE NULLIF(UPPER(TRIM(c.phone_3)), '') IS NOT NULL
UNION ALL
SELECT c.customer_id                         customer_id
     , c.nrm_customer_name                   customer_name
     , TRIM(c.country)                       phone_country
     , c.nrm_country_code                    country_code
     , c.nrm_phone_code                      international_phone_code
     , c.fax                                 phone_raw
     , 'fax'                                 phone_type
     , '_FAX'                                suffix
  FROM src_fin_customer c
 WHERE NULLIF(UPPER(TRIM(c.fax)), '') IS NOT NULL
       )
     , cte_phone_split
    AS (
SELECT DISTINCT
       p.customer_id                                                       customer_id
     , p.customer_name                                                     customer_name
     , p.phone_country                                                     phone_country
     , p.country_code                                                      country_code
     , TRIM(REGEXP_REPLACE(p.international_phone_code, '[^0-9]', ''))      international_phone_code
     , LTRIM(TRIM(REGEXP_REPLACE(u.phone, '[^0-9]', '')), '0')             phone_number_raw
     , p.phone_type                                                        phone_type
     , p.suffix                                                            suffix
  FROM cte_customer_phone p
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
  FROM cte_phone_split                 s
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
  FROM cte_cleaned                     t
      )
SELECT s.customer_id                                                       customer_id
     , s.customer_name                                                     customer_name
     , TRIM(s.customer_id) || s.suffix || '_' || ROW_NUMBER() OVER (
           PARTITION BY s.customer_id, s.suffix
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
     , CASE
         WHEN s.phone_number_raw LIKE s.international_phone_code || '%'
         THEN REGEXP_REPLACE(s.phone_number_raw, '^' || s.international_phone_code, '')
         ELSE s.phone_number_raw
       END                                                                 formatted_phone_number
     , NULL                                                                phone_number_extension
     , s.drv_phone_device_type                                             phone_device_type
     , 'Yes'                                                               is_public
     , CASE WHEN s.phone_type = 'primary' THEN 'Yes' ELSE 'No' END         is_primary
     , s.phone_type                                                        phone_type
     , NULL                                                                use_for
     , NULL                                                                use_for_tenanted
     , NULL                                                                tenant_formatted_phone
     , NULL                                                                international_formatted_phone
     , NULL                                                                delete_flag
     , NULL                                                                do_not_replace_all
     , NULL                                                                phone_comment
     , NULL                                                                phone
  FROM cte_phone_parse                 s
 WHERE NULLIF(TRIM(s.phone_number_raw), '') IS NOT NULL
;
