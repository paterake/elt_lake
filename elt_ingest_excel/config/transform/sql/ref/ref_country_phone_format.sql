DROP TABLE IF EXISTS ref_country_phone_format
;
CREATE TABLE ref_country_phone_format
    AS
SELECT
       *
  FROM (VALUES

        -- Country, International Phone Code, and validation messages

          ('Afghanistan'              , '93' , '2 digits, no special characters'                                                       , '7 digits only, no special characters'                                                          , '2-3 digits, no special characters'                                                       , '6-7 digits only, no special characters')
        , ('Åland Islands'            , '358', '1-3 digits, no special characters, may be preceded by ''0'''                           , '4-8 digits only, no special characters'                                                        , '2-4 digits, no special characters, may be preceded by ''0'''                           , '4-8 digits only, no special characters')
        , ('Albania'                  , '355', '1-3 digits, no special characters, may be preceded by ''0'''                           , '4-7 digits only, no special characters'                                                        , '1-3 digits, no special characters, may be preceded by ''0'''                           , '4-7 digits only, no special characters')
        , ('Algeria'                  , '213', '2 digits, no special characters'                                                       , '6 digits only, no special characters'                                                          , '1-3 digits, no special characters'                                                       , '6-8 digits only, no special characters')
        , ('American Samoa'           , '1'  , '3 digits, no special characters'                                                       , '3 digits + optional dash (or dot) + 4 digits'                                                  , '3 digits, no special characters'                                                         , '3 digits + optional dash (or dot) + 4 digits')
        , ('Andorra'                  , '376', 'area code not used'                                                                    , '6 digits only, no special characters'                                                          , 'area code not used'                                                                      , '6 digits only, no special characters')
        , ('Angola'                   , '244', '2-3 digits, no special characters'                                                     , '6-7 digits only, no special characters'                                                        , '2-3 digits, no special characters'                                                       , '6-7 digits only, no special characters')
        , ('Anguilla'                 , '1'  , '3 digits, no special characters'                                                       , '3 digits + optional dash (or dot) + 4 digits'                                                  , '3 digits, no special characters'                                                         , '3 digits + optional dash (or dot) + 4 digits')
        , ('Antigua and Barbuda'      , '1'  , '3 digits, no special characters'                                                       , '3 digits + optional dash (or dot) + 4 digits'                                                  , '3 digits, no special characters'                                                         , '3 digits + optional dash (or dot) + 4 digits')
        , ('Argentina'                , '54' , '2-4 digits, no special characters, may be preceded by ''0'''                           , '6-8 digits only, no special characters'                                                        , '2-4 digits, no special characters, may be preceded by ''0'''                           , '6-8 digits only, no special characters')
        , ('Armenia'                  , '374', '2-3 digits, no special characters'                                                     , '5-6 digits only, no special characters'                                                        , '2 digits, no special characters'                                                         , '6 digits only, no special characters')
        , ('Aruba'                    , '297', 'area code not used'                                                                    , '3 digits + optional dash (or dot) + 4 digits'                                                  , '3 digits, no special characters'                                                         , '3 digits + optional dash (or dot) + 4 digits')

        -- Key reference markets
        , ('France'                   , '33' , '1 digit, may be preceded by ''0'''                                                     , '8-10 digits only, no special characters'                                                       , '1 digit, may be preceded by ''0'''                                                     , '8-10 digits only, no special characters')
        , ('Germany'                  , '49' , '2-5 digits, no special characters, may be preceded by ''0'''                           , '3-11 digits only, no special characters'                                                       , '2-4 digits, no special characters, may be preceded by ''0'''                           , '6-11 digits only, no special characters')
        , ('Ireland'                  , '353', '1-3 digits, no special characters, may be preceded by ''0'''                           , '5-7 digits only, no special characters'                                                        , '2 digits, no special characters, may be preceded by ''0'''                             , '5-7 digits only, no special characters')
        , ('United Kingdom'           , '44' , '2-5 digits, no special characters, may be preceded by ''0'''                           , '4-8 digits only, no special characters'                                                        , '2-5 digits, no special characters, may be preceded by ''0'''                           , '5-8 or 10 digits, no special characters, may be preceded by ''0'' if followed by 10 digits')
        , ('United States of America' , '1'  , '3 digits, no special characters'                                                       , '3 digits + optional dash (or dot) + 4 digits'                                                  , '3 digits, no special characters'                                                         , '3 digits + optional dash (or dot) + 4 digits')

) AS t(
    country_name
  , international_phone_code_digits
  , area_code_validation_message
  , phone_number_validation_message
  , mobile_area_code_message
  , mobile_phone_number_message
)
;

