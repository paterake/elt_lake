DROP TABLE IF EXISTS workday_customer_credit_card
;
CREATE TABLE workday_customer_credit_card
    AS
SELECT
       customer_id                                   customer_id
     , TRIM(customer_name)                           customer_name
     , NULL                                          merchant_customer_profile_id
     , NULL                                          primary_card
     , NULL                                          merchant_account
     , NULL                                          credit_card_type
     , NULL                                          first_name
     , NULL                                          last_name
     , NULL                                          expiration_date
     , NULL                                          last_4_digits_of_credit_card_number
     , NULL                                          customer_profile_id
  FROM src_fin_customer
 WHERE 1 = 0
;
