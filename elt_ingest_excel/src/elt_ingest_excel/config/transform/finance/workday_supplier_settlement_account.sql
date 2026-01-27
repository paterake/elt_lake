DROP TABLE IF EXISTS workday_supplier_settlement_account
;
CREATE TABLE workday_supplier_settlement_account AS
SELECT
       TRIM(vendor_id)                                                    supplier_id
     , TRIM(vendor_name)                                                  supplier_name
     , TRIM(vendor_id) || '_BANK'                                         settlement_bank_account_id
     , COALESCE(TRIM(UPPER(bank_country_code)), 'GB')                     bank_country
     , COALESCE(TRIM(currencyid), TRIM(currency_id), 'GBP')               currency
     , CASE UPPER(TRIM(COALESCE(eft_account_type, 'C')))
         WHEN 'C'        THEN 'CHECKING'
         WHEN 'S'        THEN 'SAVINGS'
         WHEN 'CHECKING' THEN 'CHECKING'
         WHEN 'SAVINGS'  THEN 'SAVINGS'
         ELSE 'CHECKING'
       END                                                                bank_account_type
     , TRIM(bank_name)                                                    bank_name
     , TRIM(vendor_check_name)                                            name_on_account
     , TRIM(REPLACE(eft_bank_account, ' ', ''))                           bank_account_number
     , TRIM(vendor_short_name) || ' Bank'                                 bank_account_nickname
     , CASE
         WHEN COALESCE(TRIM(UPPER(bank_country_code)), 'GB') IN ('GB', 'IE', 'FR', 'DE', 'ES', 'IT', 'NL', 'BE', 'PT', 'AT', 'SE', 'DK', 'FI')
         THEN TRIM(REPLACE(REPLACE(eft_bank_code, ' ', ''), '-', ''))
         WHEN COALESCE(TRIM(UPPER(bank_country_code)), 'GB') = 'US'
         THEN TRIM(REPLACE(REPLACE(eft_transit_routing_no, ' ', ''), '-', ''))
         ELSE TRIM(REPLACE(REPLACE(eft_bank_code, ' ', ''), '-', ''))
       END                                                                routing_number_bank_code
     , TRIM(REPLACE(REPLACE(UPPER(iban), ' ', ''), '-', ''))              iban
     , TRIM(UPPER(swift_address))                                         swift_bank_identification_code
     , TRIM(building_society_roll_no)                                     roll_number
     , TRIM(eft_bank_check_digit)                                         check_digit
     , TRIM(eft_bank_branch_code)                                         branch_id
     , TRIM(eft_bank_branch)                                              branch_name
     , CASE UPPER(TRIM(COALESCE(eft_transfer_method, 'ACH')))
         WHEN 'ACH'        THEN 'ACH'
         WHEN 'WIRE'       THEN 'Wire'
         WHEN 'ELECTRONIC' THEN 'ACH'
         ELSE 'ACH'
       END                                                                accepts_payment_types_plus
     , CASE UPPER(TRIM(COALESCE(eft_transfer_method, 'ACH')))
         WHEN 'ACH'        THEN 'ACH'
         WHEN 'WIRE'       THEN 'Wire'
         WHEN 'ELECTRONIC' THEN 'ACH'
         ELSE 'ACH'
       END                                                                payment_types_plus
     , FALSE                                                              for_supplier_connections_only
     , CASE WHEN eft_pre_note_date IS NOT NULL THEN TRUE ELSE FALSE END   requires_prenote
     , CASE WHEN eft_pre_note_date IS NOT NULL THEN 'ACH' ELSE NULL END   payment_type_prenote
     , CASE 
        WHEN TRIM(UPPER(inactive))      = UPPER('YES')
          OR TRIM(UPPER(vendor_status)) = UPPER('Inactive')
        THEN TRUE 
        ELSE FALSE 
       END                                                                inactive
     , TRIM(additional_information)                                       bank_instructions
  FROM src_fin_supplier
 WHERE (eft_bank_account IS NOT NULL OR iban IS NOT NULL)
   AND (TRIM(eft_bank_account) != '' OR TRIM(iban) != '')
;
