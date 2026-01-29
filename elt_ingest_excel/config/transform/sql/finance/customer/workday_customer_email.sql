DROP TABLE IF EXISTS workday_customer_email
;
CREATE TABLE workday_customer_email
    AS
-- Email To Address (Primary)
SELECT
       TRIM(customer_id)                                               customer_id
     , TRIM(customer_name)                                             customer_name
     , TRIM(customer_id) || '_EM1'                                     email_id
     , TRIM(LOWER(email_to_address))                                   email_address
     , NULL                                                            email_comment
     , 'Yes'                                                           is_public
     , 'Yes'                                                           is_primary
     , 'Business'                                                      email_type
     , 'Business'                                                      use_for
     , NULL                                                            use_for_tenanted
     , NULL                                                            delete_flag
     , NULL                                                            do_not_replace_all
     , NULL                                                            additional_comment
     , TRIM(LOWER(email_to_address))                                   email
  FROM src_fin_customer
 WHERE email_to_address IS NOT NULL
   AND TRIM(email_to_address) != ''
   AND email_to_address ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

UNION ALL

-- Email Cc Address
SELECT
       TRIM(customer_id)                                               customer_id
     , TRIM(customer_name)                                             customer_name
     , TRIM(customer_id) || '_EM2'                                     email_id
     , TRIM(LOWER(email_cc_address))                                   email_address
     , NULL                                                            email_comment
     , 'Yes'                                                           is_public
     , 'No'                                                            is_primary
     , 'Business'                                                      email_type
     , 'Business'                                                      use_for
     , NULL                                                            use_for_tenanted
     , NULL                                                            delete_flag
     , NULL                                                            do_not_replace_all
     , NULL                                                            additional_comment
     , TRIM(LOWER(email_cc_address))                                   email
  FROM src_fin_customer
 WHERE email_cc_address IS NOT NULL
   AND TRIM(email_cc_address) != ''
   AND email_cc_address ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

UNION ALL

-- Email Bcc Address
SELECT
       TRIM(customer_id)                                               customer_id
     , TRIM(customer_name)                                             customer_name
     , TRIM(customer_id) || '_EM3'                                     email_id
     , TRIM(LOWER(email_bcc_address))                                  email_address
     , NULL                                                            email_comment
     , 'Yes'                                                           is_public
     , 'No'                                                            is_primary
     , 'Business'                                                      email_type
     , 'Business'                                                      use_for
     , NULL                                                            use_for_tenanted
     , NULL                                                            delete_flag
     , NULL                                                            do_not_replace_all
     , NULL                                                            additional_comment
     , TRIM(LOWER(email_bcc_address))                                  email
  FROM src_fin_customer
 WHERE email_bcc_address IS NOT NULL
   AND TRIM(email_bcc_address) != ''
   AND email_bcc_address ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
;
