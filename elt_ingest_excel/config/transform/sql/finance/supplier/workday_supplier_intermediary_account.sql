DROP TABLE IF EXISTS workday_supplier_intermediary_account
;
CREATE TABLE workday_supplier_intermediary_account 
    AS
SELECT
       s.supplier_id || '_BANK'                                      settlement_bank_account_id
     , s.nrm_vendor_name                                            supplier_name
     , s.supplier_id                                                supplier_id
     , s.supplier_id || '_INTBANK'                                  intermediary_bank_account_id
     , NULL                                                       bank_country
     , s.nrm_currency_code                                            currency
     , 'CHECKING'                                                 bank_account_type
     , NULL                                                       bank_name
     , NULL                                                       name_on_account
     , NULL                                                       bank_account_number
     , TRIM(s.vendor_short_name) || ' Intermediary'                 bank_account_nickname
     , TRIM(s.central_bank_code)                                    routing_number_bank_code
     , NULL                                                       iban
     , NULL                                                       swift_bank_identification_code
     , NULL                                                       roll_number
     , NULL                                                       check_digit
     , NULL                                                       branch_id
     , NULL                                                       branch_name
     , CASE
         WHEN UPPER(TRIM(s.vendor_status)) = 'ACTIVE'
         THEN 'No'
         ELSE 'Yes'
       END                                                         inactive
     , NULL                                                       bank_instructions
  FROM src_fin_supplier s
 WHERE s.central_bank_code IS NOT NULL
   AND TRIM(s.central_bank_code) != ''
;
