DROP TABLE IF EXISTS workday_supplier_settlement_account
;
CREATE TABLE workday_supplier_settlement_account 
    AS
  WITH cte_supplier_distinct
    AS (    
SELECT DISTINCT
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
 WHERE COALESCE(u.bank.nrm_bank_account_number, u.bank.nrm_bank_iban)  IS NOT NULL
   AND NULLIF(TRIM(u.bank.nrm_bank_name), '')                          IS NOT NULL
       )
     , cte_supplier_rank
    AS (
SELECT ROW_NUMBER() OVER (PARTITION BY t.supplier_id, COALESCE(t.bank_account_number, t.bank_iban)
                          ORDER BY t.bank_name
                   ) rnk  
     , t.*
  FROM cte_supplier_distinct t
       )
SELECT 
       t.supplier_id
     , t.supplier_name
     , t.settlement_bank_account_id
     , t.bank_country
     , t.currency
     , t.bank_account_type
     , t.bank_name
     , t.bank_account_name
     , t.bank_account_number
     , t.bank_account_nickname
     , t.bank_code_routing_number
     , t.bank_iban
     , t.bank_swift_code
     , t.bank_roll_number
     , t.bank_check_digit
     , t.bank_branch_id
     , t.bank_branch_name
     , t.accepts_payment_types_plus
     , t.payment_types_plus
     , t.for_supplier_connections_only
     , t.requires_prenote
     , t.payment_type_prenote
     , t.inactive
     , t.bank_instructions
  FROM cte_supplier_rank t
 WHERE t.rnk = 1
;
