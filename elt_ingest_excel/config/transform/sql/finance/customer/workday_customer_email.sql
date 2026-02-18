DROP TABLE IF EXISTS workday_customer_email
;
CREATE TABLE workday_customer_email AS
  WITH cte_customer_email
    AS (
SELECT c.customer_id                                  customer_id
     , c.nrm_customer_name                            customer_name
     , c.email_to_address                             email_raw
     , 'to'                                           email_type
     , '_EM1'                                         suffix
  FROM src_fin_customer c
 WHERE NULLIF(UPPER(TRIM(c.email_to_address)), '')    IS NOT NULL
UNION ALL
SELECT c.customer_id                                  customer_id
     , c.nrm_customer_name                            customer_name
     , c.email_cc_address                             email_raw
     , 'cc'                                           email_type
     , '_EM2'                                         suffix
  FROM src_fin_customer c
 WHERE NULLIF(UPPER(TRIM(c.email_cc_address)), '')   IS NOT NULL
UNION ALL
SELECT c.customer_id                                  customer_id
     , c.nrm_customer_name                            customer_name
     , c.email_bcc_address                            email_raw
     , 'bcc'                                          email_type
     , '_EM3'                                         suffix
  FROM src_fin_customer c
 WHERE NULLIF(UPPER(TRIM(c.email_bcc_address)), '')   IS NOT NULL
       )
     , cte_email_split
    AS (
SELECT e.customer_id                          customer_id
     , e.customer_name                        customer_name
     , TRIM(u.email)                          email_address
     , e.email_type                           email_type
     , e.suffix                               suffix
  FROM cte_customer_email e
     , UNNEST(STRING_SPLIT(e.email_raw, ';')) u(email)
       )
     , cte_email_rnk
    AS (
SELECT s.customer_id                          customer_id
     , s.customer_name                        customer_name
     , s.email_address                        email_address
     , s.email_type                           email_type
     , s.suffix                               suffix
     , ROW_NUMBER() OVER (
           PARTITION BY s.customer_id, s.email_type
               ORDER BY s.email_address
       )                                      email_rank
  FROM cte_email_split s
       )
SELECT s.customer_id                                                     customer_id
     , s.customer_name                                                   customer_name
     , TRIM(s.customer_id) || s.suffix || '_' || ROW_NUMBER() OVER (
           PARTITION BY s.customer_id, s.suffix ORDER BY s.email_address
       )                                                                 email_id
     , TRIM(LOWER(s.email_address))                                      email_address
     , NULL                                                              email_comment
     , 'Yes'                                                             is_public
     , CASE WHEN s.email_type = 'to' AND s.email_rank = 1
            THEN 'Yes' ELSE 'No' END                                      is_primary
     , s.email_type                                                      email_type
     , 'Business'                                                        use_for
     , NULL                                                              use_for_tenanted
     , NULL                                                              delete_flag
     , NULL                                                              do_not_replace_all
     , NULL                                                              additional_comment
     , TRIM(LOWER(s.email_address))                                      email
  FROM cte_email_rnk s
 WHERE NULLIF(TRIM(s.email_address), '') IS NOT NULL
   AND s.email_address ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
;
