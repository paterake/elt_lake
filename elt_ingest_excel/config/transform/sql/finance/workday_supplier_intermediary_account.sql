DROP TABLE IF EXISTS workday_supplier_intermediary_account
;
CREATE TABLE workday_supplier_intermediary_account 
    AS
SELECT
       TRIM(supplier_id) || '_BANK'                               settlement_bank_account_id
     , TRIM(vendor_name)                                          supplier_name
     , TRIM(supplier_id)                                          supplier_id
     , TRIM(supplier_id) || '_INTBANK'                            intermediary_bank_account_id
     , NULL                                                       bank_country
     , COALESCE(TRIM(currencyid), TRIM(currency_id), 'GBP')       currency
     , 'CHECKING'                                                 bank_account_type
     , NULL                                                       bank_name
     , NULL                                                       name_on_account
     , NULL                                                       bank_account_number
     , TRIM(vendor_short_name) || ' Intermediary'                 bank_account_nickname
     , TRIM(central_bank_code)                                    routing_number_bank_code
     , NULL                                                       iban
     , NULL                                                       swift_bank_identification_code
     , NULL                                                       roll_number
     , NULL                                                       check_digit
     , NULL                                                       branch_id
     , NULL                                                       branch_name
     , FALSE                                                      inactive
     , NULL                                                       bank_instructions
  FROM src_fin_supplier
 WHERE central_bank_code IS NOT NULL
   AND TRIM(central_bank_code) != ''
;
