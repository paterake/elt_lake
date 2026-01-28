DROP TABLE IF EXISTS workday_supplier_email
;
CREATE TABLE workday_supplier_email 
    AS
-- Email To Address (Primary)
SELECT
       TRIM(supplier_id)                                          supplier_id
     , TRIM(vendor_name)                                          supplier_name
     , TRIM(LOWER(email_to_address))                              email_address
     , NULL                                                       email_comment
     , TRIM(supplier_id) || '_EM1'                                email_id
     , 'Yes'                                                      public_flag
     , 'Yes'                                                      primary_flag
     , 'Yes'                                                      default_po
     , 'Business'                                                 email_type
     , 'Business'                                                 use_for
     , NULL                                                       use_for_tenanted
     , NULL                                                       delete_flag
     , NULL                                                       do_not_replace_all
     , NULL                                                       additional_comments
     , TRIM(LOWER(email_to_address))                              email
  FROM src_fin_supplier
 WHERE email_to_address IS NOT NULL
   AND TRIM(email_to_address) != ''
   AND email_to_address ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

UNION ALL

-- Email Cc Address
SELECT
       TRIM(supplier_id)                                          supplier_id
     , TRIM(vendor_name)                                          supplier_name
     , TRIM(LOWER(email_cc_address))                              email_address
     , NULL                                                       email_comment
     , TRIM(supplier_id) || '_EM2'                                email_id
     , 'Yes'                                                      public_flag
     , 'No'                                                       primary_flag
     , 'No'                                                       default_po
     , 'Business'                                                 email_type
     , 'Business'                                                 use_for
     , NULL                                                       use_for_tenanted
     , NULL                                                       delete_flag
     , NULL                                                       do_not_replace_all
     , NULL                                                       additional_comments
     , TRIM(LOWER(email_cc_address))                              email
  FROM src_fin_supplier
 WHERE email_cc_address IS NOT NULL
   AND TRIM(email_cc_address) != ''
   AND email_cc_address ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

UNION ALL

-- Email Bcc Address
SELECT
       TRIM(supplier_id)                                          supplier_id
     , TRIM(vendor_name)                                          supplier_name
     , TRIM(LOWER(email_bcc_address))                             email_address
     , NULL                                                       email_comment
     , TRIM(supplier_id) || '_EM3'                                email_id
     , 'Yes'                                                      public_flag
     , 'No'                                                       primary_flag
     , 'No'                                                       default_po
     , 'Business'                                                 email_type
     , 'Business'                                                 use_for
     , NULL                                                       use_for_tenanted
     , NULL                                                       delete_flag
     , NULL                                                       do_not_replace_all
     , NULL                                                       additional_comments
     , TRIM(LOWER(email_bcc_address))                             email
  FROM src_fin_supplier
 WHERE email_bcc_address IS NOT NULL
   AND TRIM(email_bcc_address) != ''
   AND email_bcc_address ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
;
