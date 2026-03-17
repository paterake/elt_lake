DROP TABLE IF EXISTS src_hcm_contingent_worker
;
CREATE TABLE src_hcm_contingent_worker
    AS
  WITH cte_contingent_worker_dedup
    AS (
SELECT *
     , ROW_NUMBER() OVER (ORDER BY username, user_id) + 100000  row_id
  FROM src_hcm_contingent_worker_raw
 WHERE data_rnk = 1
       )
SELECT
       'CW-' || LPAD(row_id::VARCHAR, 6, '0')                              contingent_worker_id
     , COALESCE(l.target_value, 'Wembley Stadium')                         nrm_location
     , COALESCE(rw.mapped_value, 'Sole Trader Staff')                      nrm_worker_type
     , t.*
  FROM 
       cte_contingent_worker_dedup        t
       LEFT OUTER JOIN 
       ref_location_mapping               l
          ON l.source_column              = 'location'
         AND UPPER(l.source_value)        = UPPER(COALESCE(NULLIF(TRIM(t.location), ''), 'Wembley Stadium'))
       LEFT OUTER JOIN
       ref_worker_type_mapping            rw
          ON UPPER(rw.user_type)          = UPPER(COALESCE(NULLIF(TRIM(t.user_type)   , ''), 'NULL'))
         AND UPPER(rw.department_1)       = UPPER(COALESCE(NULLIF(TRIM(t.department_1), ''), 'NULL'))
 WHERE 
       1 = 1
   AND COALESCE(NULLIF(UPPER(TRIM(t.location))    , ''), 'NULL')  NOT IN ('COUNTY', 'SERVICE_ACCOUNT', 'SERVICE ACCOUNT')
   AND COALESCE(NULLIF(UPPER(TRIM(t.department_1)), ''), 'NULL')  NOT IN ('COUNTY', 'SERVICE_ACCOUNT', 'SERVICE ACCOUNT')
   AND COALESCE(NULLIF(UPPER(TRIM(t.user_type))   , ''), 'NULL')  NOT IN ('COUNTY', 'SERVICE_ACCOUNT', 'SERVICE ACCOUNT')
   AND NOT (
       UPPER(TRIM(nrm_first_name))                                LIKE '%ROOM%'
    OR UPPER(TRIM(nrm_last_name ))                                LIKE '%ROOM%'
       )
   AND NOT (
       UPPER(TRIM(nrm_first_name))                                LIKE '%APP%'
   AND UPPER(TRIM(nrm_last_name ))                                LIKE '%DEV%'
       )
;
