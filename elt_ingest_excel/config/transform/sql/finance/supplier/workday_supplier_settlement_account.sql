DROP TABLE IF EXISTS workday_supplier_settlement_account
;
CREATE TABLE workday_supplier_settlement_account 
    AS
SELECT
       s.supplier_id                                                       supplier_id
     , s.nrm_vendor_name                                                    supplier_name
     , TRIM(s.eft_bank_account)                                             settlement_bank_account_id
     , s.nrm_country_name                                                   bank_country
     , s.nrm_currency_code                                                    currency
     , TRIM(s.eft_account_type)                                             bank_account_type
     , TRIM(s.bank_name)                                                    bank_name
     , TRIM(s.vendor_check_name)                                            name_on_account
     , TRIM(REPLACE(s.eft_bank_account, ' ', ''))                           bank_account_number
     , TRIM(s.vendor_short_name) || ' Bank'                                 bank_account_nickname
     , CASE
         WHEN s.nrm_country_code IN ('GB', 'IE', 'FR', 'DE', 'ES', 'IT', 'NL', 'BE', 'PT', 'AT', 'SE', 'DK', 'FI')
         THEN TRIM(REPLACE(REPLACE(s.eft_bank_code, ' ', ''), '-', ''))
         WHEN s.nrm_country_code = 'US'
         THEN TRIM(REPLACE(REPLACE(s.eft_transit_routing_no, ' ', ''), '-', ''))
         ELSE TRIM(REPLACE(REPLACE(s.eft_bank_code, ' ', ''), '-', ''))
       END                                                                routing_number_bank_code
     , TRIM(REPLACE(REPLACE(UPPER(s.iban), ' ', ''), '-', ''))              iban
     , TRIM(UPPER(s.swift_address))                                         swift_bank_identification_code
     , TRIM(s.building_society_roll_no)                                     roll_number
     , TRIM(s.eft_bank_check_digit)                                         check_digit
     , TRIM(s.eft_bank_branch_code)                                         branch_id
     , TRIM(s.eft_bank_branch)                                              branch_name
     , TRIM(s.eft_transfer_method)                                          accepts_payment_types_plus
     , TRIM(s.eft_transfer_method)                                          payment_types_plus
     , NULL                                                               for_supplier_connections_only
     , NULL                                                               requires_prenote
     , NULL                                                               payment_type_prenote
     , CASE
         WHEN UPPER(TRIM(s.vendor_status)) = 'ACTIVE'
         THEN 'No'
         ELSE 'Yes'
       END                                                                inactive
     , TRIM(s.additional_information)                                       bank_instructions
  FROM src_fin_supplier s
 WHERE (s.eft_bank_account IS NOT NULL OR s.iban IS NOT NULL)
   AND (TRIM(s.eft_bank_account) != '' OR TRIM(s.iban) != '')
;
