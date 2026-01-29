DROP TABLE IF EXISTS workday_supplier_currencies
;
CREATE TABLE workday_supplier_currencies 
    AS
SELECT
       TRIM(supplier_id)                           supplier_id
     , TRIM(vendor_name)                           supplier_name
     , CASE
         WHEN NULLIF(TRIM(currency_id), '') IS NOT NULL
          AND NULLIF(TRIM(currencyid ), '') IS NOT NULL
          AND TRIM(currency_id) != TRIM(currencyid)
         THEN TRIM(currency_id) || '|' || TRIM(currencyid)
         ELSE COALESCE(NULLIF(TRIM(currency_id), ''), NULLIF(TRIM(currencyid), ''))
       END                                         accepted_currencies_plus
     , COALESCE(NULLIF(TRIM(currency_id), ''), NULLIF(TRIM(currencyid), 'GBP'))
                                                   default_currency
  FROM src_fin_supplier
;
