DROP TABLE IF EXISTS workday_customer_intermediary_account
;
CREATE TABLE workday_customer_intermediary_account
    AS
SELECT
       TRIM(customer_id) || '_BANK'                  settlement_bank_account_id
     , TRIM(customer_name)                           customer_name
     , TRIM(customer_id)                             customer_id
     , TRIM(customer_id) || '_INTBANK'               intermediary_bank_account_id
     , 'GB'                                          bank_country
     , 'GBP'                                         currency
     , 'CHECKING'                                    bank_account_type
     , NULL                                          bank_name
     , NULL                                          name_on_account
     , NULL                                          bank_account_number
     , TRIM(short_name) || ' Intermediary'           bank_account_nickname
     , NULL                                          routing_transit_number
     , NULL                                          iban
     , NULL                                          swift_bank_identification_code
     , NULL                                          roll_number
     , NULL                                          check_digit
     , NULL                                          branch_id
     , NULL                                          branch_name
     , CASE
         WHEN UPPER(TRIM(inactive)) = 'NO'           THEN 'No'
         ELSE 'Yes'
       END                                           inactive
     , NULL                                          bank_instructions
  FROM src_fin_customer
 WHERE checkbook_id IS NOT NULL
   AND TRIM(checkbook_id) != ''
;
