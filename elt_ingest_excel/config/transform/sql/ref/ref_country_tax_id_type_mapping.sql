DROP TABLE IF EXISTS ref_country_tax_id_type_mapping
;
CREATE TABLE ref_country_tax_id_type_mapping
    AS
SELECT
       *
  FROM (VALUES
        -- United Kingdom: allowed list from workbook; no default marker (pattern-derived)
          ('GB', 'Company Number'                                                     , FALSE)
        , ('GB', 'COTAX Reference'                                                    , FALSE)
        , ('GB', 'DUNS'                                                               , FALSE)
        , ('GB', 'Employer Accounts Office Reference Number'                          , FALSE)
        , ('GB', 'ECON'                                                               , FALSE)
        , ('GB', 'E-File VAT Registration Number'                                     , FALSE)
        , ('GB', 'EORI Code - Economic Operator Registration and Identification code' , FALSE)
        , ('GB', 'HMRC Office Number'                                                 , FALSE)
        , ('GB', 'Legal form of the Company'                                          , FALSE)
        , ('GB', 'NINO - National Insurance Number'                                   , FALSE)
        , ('GB', 'Employer PAYE Reference'                                            , FALSE)
        , ('GB', 'UTR - Unique Taxpayer Reference'                                    , FALSE)
        , ('GB', 'VAT Reg No'                                                         , FALSE)
        -- Non-UK defaults (extend as needed)
        , ('US', 'Employer ID Number'                                                 , TRUE )
        , ('DE', 'USt-IdNr (VAT)'                                                     , TRUE )
        , ('FR', 'SIRET'                                                              , TRUE )
        , ('IE', 'VAT No'                                                             , TRUE )
        , ('CH', 'UID-number'                                                         , TRUE )
        , ('AU', 'ABN'                                                                , TRUE )
       ) AS t(country_code, tax_id_type_label, is_default)
;
