DROP TABLE IF EXISTS workday_customer_intermediary_account
;
CREATE TABLE workday_customer_intermediary_account
    AS
SELECT
       TRIM(c.customer_id) || '_BANK'                settlement_bank_account_id
     , TRIM(c.customer_name)                         customer_name
     , c.customer_id                                 customer_id
     , TRIM(c.customer_id) || '_INTBANK'             intermediary_bank_account_id
     , 'GB'                                          bank_country
     , 'GBP'                                         currency
     , 'CHECKING'                                    bank_account_type
     , NULL                                          bank_name
     , NULL                                          name_on_account
     , NULL                                          bank_account_number
     , TRIM(c.short_name) || ' Intermediary'         bank_account_nickname
     , NULL                                          routing_transit_number
     , NULL                                          iban
     , NULL                                          swift_bank_identification_code
     , NULL                                          roll_number
     , NULL                                          check_digit
     , NULL                                          branch_id
     , NULL                                          branch_name
     , CASE
         WHEN UPPER(TRIM(c.inactive)) = 'NO'         THEN 'No'
         ELSE 'Yes'
       END                                           inactive
     , NULL                                          bank_instructions
  FROM src_fin_customer                c
 WHERE c.checkbook_id IS NOT NULL
   AND TRIM(c.checkbook_id) != ''
;
