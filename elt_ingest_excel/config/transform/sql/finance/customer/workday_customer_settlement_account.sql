DROP TABLE IF EXISTS workday_customer_settlement_account
;
CREATE TABLE workday_customer_settlement_account
    AS
SELECT
       TRIM(customer_id)                             customer_id
     , TRIM(customer_name)                           customer_name
     , TRIM(customer_id) || '_BANK'                  settlement_bank_account_id
     , 'GB'                                          country
     , 'GBP'                                         currency
     , TRIM(short_name) || ' Bank'                   bank_account_nickname
     , 'CHECKING'                                    bank_account_type
     , NULL                                          bank_name
     , NULL                                          routing_transit_number
     , NULL                                          branch_id
     , NULL                                          branch_name
     , NULL                                          bank_account_number
     , NULL                                          check_digit
     , TRIM(customer_name)                           name_on_account
     , NULL                                          roll_number
     , NULL                                          iban
     , NULL                                          swift_bank_identification_code
     , 'ACH'                                         accepts_payment_types
     , 'ACH'                                         payment_types
     , NULL                                          for_supplier_connections_only
     , NULL                                          requires_prenote
     , NULL                                          payment_type_prenote
     , CASE
         WHEN UPPER(TRIM(inactive)) = 'NO'           THEN 'No'
         ELSE 'Yes'
       END                                           inactive
     , NULL                                          bank_instructions
  FROM src_fin_customer
 WHERE checkbook_id IS NOT NULL
   AND TRIM(checkbook_id) != ''
;
