DROP TABLE IF EXISTS workday_supplier_email
;
CREATE TABLE workday_supplier_email AS
  WITH cte_supplier_email
    AS (
SELECT s.supplier_id                          supplier_id
     , s.nrm_vendor_name                      supplier_name
     , s.email_to_address                     email_raw
     , 'primary'                              email_type
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

SELECT e.supplier_id                                                     supplier_id
     , e.supplier_name                                                   supplier_name
     , TRIM(LOWER(e.email_raw))                                          email_address
     , NULL                                                              email_comment
     , e.supplier_id || e.suffix                                         email_id
     , 'Yes'                                                             public_flag
     , CASE WHEN e.email_type = 'primary' THEN 'Yes' ELSE 'No' END       primary_flag
     , CASE WHEN e.email_type = 'primary' THEN 'Yes' ELSE 'No' END       default_po
     , e.email_type                                                      email_type
     , 'Business'                                                        use_for
     , NULL                                                              use_for_tenanted
     , NULL                                                              delete_flag
     , NULL                                                              do_not_replace_all
     , NULL                                                              additional_comments
     , TRIM(LOWER(e.email_raw))                                          email
  FROM cte_supplier_email e
 WHERE e.email_raw ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
;
