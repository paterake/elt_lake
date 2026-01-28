DROP TABLE IF EXISTS workday_supplier_currencies
;
CREATE TABLE workday_supplier_currencies 
    AS
SELECT
       TRIM(supplier_id)                           supplier_id
     , TRIM(vendor_name)                           supplier_name
     , COALESCE(
         NULLIF(TRIM(currencyid), '')
       , NULLIF(TRIM(currency_id), '')
       , 'GBP'
       )                                           accepted_currencies_plus
     , COALESCE(
         NULLIF(TRIM(currencyid), '')
       , NULLIF(TRIM(currency_id), '')
       , 'GBP'
       )                                           default_currency
  FROM src_fin_supplier
;
