DROP TABLE IF EXISTS workday_supplier_email
;
CREATE TABLE workday_supplier_email AS
  WITH cte_supplier_email
    AS (
SELECT s.supplier_id                          supplier_id
     , s.nrm_vendor_name                      supplier_name
     , s.email_to_address                     email_raw
     , 'to'                                   email_type
     , '_EM1'                                 suffix
  FROM src_fin_supplier s
 WHERE NULLIF(UPPER(TRIM(s.email_to_address)), '') IS NOT NULL
UNION ALL
SELECT s.supplier_id                          supplier_id
     , s.nrm_vendor_name                      supplier_name
     , s.email_cc_address                     email_raw
     , 'cc'                                   email_type
     , '_EM2'                                 suffix
  FROM src_fin_supplier s
 WHERE NULLIF(UPPER(TRIM(s.email_cc_address)), '') IS NOT NULL
UNION ALL
SELECT s.supplier_id                          supplier_id
     , s.nrm_vendor_name                      supplier_name
     , s.email_bcc_address                    email_raw
     , 'bcc'                                  email_type
     , '_EM3'                                 suffix
  FROM src_fin_supplier s
 WHERE NULLIF(UPPER(TRIM(s.email_bcc_address)), '') IS NOT NULL
       )
     , cte_email_split
    AS (
SELECT DISTINCT
       e.supplier_id                          supplier_id
     , e.supplier_name                        supplier_name
     , CASE
         -- Display name format 'Name <email@domain.com>': extract from inside < >
         WHEN TRIM(u.email) ~ '<[^>]+>'
         THEN REGEXP_EXTRACT(TRIM(u.email), '<([^>]+)>', 1)
         ELSE TRIM(u.email)
       END                                    email_address
     , e.email_type                           email_type
     , e.suffix                               suffix
  FROM cte_supplier_email e
       -- Normalise space-delimited multi-emails to semicolons before splitting,
       -- then split on semicolons
     , UNNEST(STRING_SPLIT(REGEXP_REPLACE(e.email_raw, '\s+', ';'),';')) u(email)
       )
     , cte_email_rnk
    AS (
SELECT s.supplier_id                          supplier_id
     , s.supplier_name                        supplier_name
     , s.email_address                        email_address
     , s.email_type                           email_type
     , s.suffix                               suffix
     , ROW_NUMBER() OVER (
           PARTITION BY s.supplier_id, s.email_type
               ORDER BY s.email_address
       )                                      email_rank
  FROM cte_email_split s
       )
SELECT s.supplier_id                                                       supplier_id
     , s.supplier_name                                                     supplier_name
     , TRIM(LOWER(s.email_address))                                        email_address
     , NULL                                                                email_comment
     , s.supplier_id || s.suffix || '_' || ROW_NUMBER() OVER (
           PARTITION BY s.supplier_id, s.suffix
               ORDER BY s.email_address
       )                                                                   email_id
     , 'Yes'                                                               public_flag
     , CASE
         WHEN s.email_type = 'to' AND s.email_rank = 1
         THEN 'Yes'
         ELSE 'No'
       END                                                                 primary_flag
     , CASE
         WHEN s.email_type = 'to' AND s.email_rank = 1
         THEN 'Yes'
         ELSE 'No'
       END                                                                 default_po
     , NULL                                                                email_type
     , 'SHIPPING|BILLING|REMIT'                                            use_for
     , NULL                                                                use_for_tenanted
     , NULL                                                                delete_flag
     , NULL                                                                do_not_replace_all
     , NULL                                                                additional_comments
     , NULL                                                                email
  FROM cte_email_rnk s
 WHERE NULLIF(TRIM(s.email_address), '') IS NOT NULL
   AND s.email_address ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
;