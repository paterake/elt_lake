DROP TABLE IF EXISTS ref_bank_sort_code_mapping
;
CREATE TABLE ref_bank_sort_code_mapping
    AS
SELECT
       *
  FROM (VALUES
          ('GB', '090128', 'Santander Bank')
        , ('GB', '070436', 'Nationwide Building Society')
        , ('GB', '236972', 'Prepay Technologies')
        , ('GB', '230580', 'Metro Bank')
        , ('GB', '040004', 'Monzo Bank')
        , ('GB', '040075', 'Modulr Finance (Revolut)')
        , ('GB', '040026', 'N26 Bank')
        , ('GB', '087199', 'Aps Financial')
        , ('GB', '608371', 'Starling Bank')
        , ('GB', '401276', 'HSBC')
        , ('GB', '231470', 'TransferWise')
        , ('GB', '202678', 'Barclays')
        , ('GB', '083210', 'Government Banking (HMRC Direct Taxes)')
        , ('GB', '774926', 'Lloyds Bank')
        , ('GB', '110001', 'Halifax (Bank of Scotland)')
        , ('GB', '166300', 'Royal Bank of Scotland')
        , ('GB', '609104', 'Standard Chartered Bank')
        , ('GB', '606004', 'National Westminster Bank')
) AS t(country_code, sort_code, bank_name)
;
