DROP TABLE IF EXISTS workday_customer_bank_account_address
;
CREATE TABLE workday_customer_bank_account_address
    AS
SELECT
       c.customer_id_name                             customer_name
     , c.customer_id                                  customer_id
     , TRIM(c.customer_id) || '_BANK'                 settlement_bank_account_id
     , NULL                                           intermediary_bank_account_id
     , TRIM(c.customer_id) || '_BANK_ADDR'            address_id
     , TRIM(c.country)                                country
     , TRIM(c.county)                                 region
     , NULL                                           subregion
     , TRIM(c.city)                                   city
     , NULL                                           submunicipality
     , TRIM(c.address_1)                              address_line_1
     , NULLIF(TRIM(c.address_2), '')                  address_line_2
     , NULLIF(TRIM(c.address_3), '')                  address_line_3
     , NULL                                           address_line_4
     , TRIM(UPPER(c.post_code))                       postal_code
     , 'Yes'                                          is_public
     , 'Yes'                                          is_primary
     , c.created_date                                 effective_date
     , TRIM(c.address_code)                           address_type
     , TRIM(c.address_code)                           use_for
     , NULL                                           use_for_tenanted
  FROM src_fin_customer                c
 WHERE c.checkbook_id IS NOT NULL
   AND TRIM(c.checkbook_id) != ''
   AND c.address_1 IS NOT NULL
   AND TRIM(c.address_1) != ''
;
