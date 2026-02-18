DROP TABLE IF EXISTS workday_supplier_currencies
;
CREATE TABLE workday_supplier_currencies 
    AS
SELECT
       s.supplier_id                                  supplier_id
     , s.nrm_vendor_name                              supplier_name
     , s.nrm_currency_code                            accepted_currencies_plus
     , s.nrm_currency_code                            default_currency
  FROM src_fin_supplier s
;
