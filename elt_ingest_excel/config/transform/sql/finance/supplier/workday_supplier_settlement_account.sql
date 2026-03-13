DROP TABLE IF EXISTS workday_supplier_settlement_account
;
CREATE TABLE workday_supplier_settlement_account 
    AS
SELECT
       t.supplier_id                            supplier_id
     , t.nrm_supplier_name                      supplier_name
     , NULL                                     settlement_bank_account_id
     , t.nrm_country_name                       bank_country
     , t.nrm_currency_code                      currency
     , u.bank.nrm_bank_account_type             bank_account_type
     , u.bank.nrm_bank_name                     bank_name
     , u.bank.nrm_bank_account_name             bank_account_name
     , u.bank.nrm_bank_account_number           bank_account_number
     , NULL                                     bank_account_nickname
     , u.bank.nrm_bank_code_routing_number      bank_code_routing_number
     , u.bank.nrm_bank_iban                     bank_iban
     , u.bank.nrm_bank_swift_code               bank_swift_code
     , u.bank.nrm_bank_roll_number              bank_roll_number
     , u.bank.nrm_bank_check_digit              bank_check_digit
     , u.bank.nrm_bank_branch_id                bank_branch_id
     , NULL                                     bank_branch_name
     , NULL                                     accepts_payment_types_plus
     , NULL                                     payment_types_plus
     , NULL                                     for_supplier_connections_only
     , NULL                                     requires_prenote
     , NULL                                     payment_type_prenote
     , NULL                                     inactive
     , NULL                                     bank_instructions
  FROM src_fin_supplier                t
     , UNNEST(nrm_array_bank) u(bank)
 WHERE COALESCE( u.bank.nrm_bank_account_number
               , u.bank.nrm_bank_iban
               )                                IS NOT NULL
   AND NULLIF(TRIM(u.bank.nrm_bank_name), '')   IS NOT NULL
;
