DROP TABLE IF EXISTS workday_customer_currencies
;
CREATE TABLE workday_customer_currencies
    AS
SELECT
       c.customer_id                                  customer_id
     , c.customer_id_name                             customer_name
     , COALESCE(rc.currency_code, 'GBP')              accepted_currencies
     , COALESCE(rc.currency_code, 'GBP')              default_currency
  FROM src_fin_customer                c
       LEFT OUTER JOIN
       ref_customer_country_language   rc
          ON rc.country_code           = COALESCE(NULLIF(UPPER(TRIM(c.country_code)), ''), 'GB')
;
