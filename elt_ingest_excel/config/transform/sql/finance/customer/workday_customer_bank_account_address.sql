DROP TABLE IF EXISTS workday_customer_bank_account_address
;
CREATE TABLE workday_customer_bank_account_address
    AS
SELECT
       TRIM(customer_name)                           customer_name
     , TRIM(customer_id)                             customer_id
     , TRIM(customer_id) || '_BANK'                  settlement_bank_account_id
     , NULL                                          intermediary_bank_account_id
     , TRIM(customer_id) || '_BANK_ADDR'             address_id
     , TRIM(country)                                 country
     , TRIM(county)                                  region
     , NULL                                          subregion
     , TRIM(city)                                    city
     , NULL                                          submunicipality
     , TRIM(address_1)                               address_line_1
     , NULLIF(TRIM(address_2), '')                   address_line_2
     , NULLIF(TRIM(address_3), '')                   address_line_3
     , NULL                                          address_line_4
     , TRIM(UPPER(post_code))                        postal_code
     , 'Yes'                                         public
     , 'Yes'                                         primary
     , created_date                                  effective_date
     , TRIM(address_code)                            type
     , TRIM(address_code)                            use_for
     , NULL                                          use_for_tenanted
  FROM src_fin_customer
 WHERE checkbook_id IS NOT NULL
   AND TRIM(checkbook_id) != ''
   AND address_1 IS NOT NULL
   AND TRIM(address_1) != ''
;
