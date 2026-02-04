DROP TABLE IF EXISTS workday_supplier_currencies
;
CREATE TABLE workday_supplier_currencies 
    AS
SELECT
       s.supplier_id                                  supplier_id
     , s.nrm_vendor_name                              supplier_name
     , CASE
         WHEN NULLIF(TRIM(s.currency_id), '')   IS NOT NULL
          AND NULLIF(TRIM(s.currencyid ), '')   IS NOT NULL
          AND TRIM(s.currency_id)               != TRIM(s.currencyid)
         THEN TRIM(s.currency_id) || '|' || TRIM(s.currencyid)
         ELSE COALESCE(NULLIF(TRIM(s.currency_id), ''), NULLIF(TRIM(s.currencyid), ''))
       END                                            accepted_currencies_plus
     , COALESCE(NULLIF(TRIM(s.currency_id), ''), NULLIF(TRIM(s.currencyid), 'GBP'))
                                                      default_currency
  FROM src_fin_supplier s
;
