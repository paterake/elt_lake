DROP TABLE IF EXISTS src_hcm_contingent_worker
;
CREATE TABLE src_hcm_contingent_worker
    AS
  WITH cte_contingent_worker_base
    AS (
SELECT * FROM hcm_contingent_worker
       )
     , cte_contingent_worker_distinct
    AS (
SELECT DISTINCT *
  FROM cte_contingent_worker_base
       )
     , cte_contingent_worker_rnk
    AS (
SELECT t.*
     , ROW_NUMBER() OVER
       (PARTITION BY username
            ORDER BY
              created_date          DESC NULLS LAST
       ) data_rnk
  FROM cte_contingent_worker_distinct t
       )
     , cte_contingent_worker
    AS (
SELECT *
     , ROW_NUMBER() OVER (ORDER BY username, user_id) + 100000  rnk
  FROM cte_contingent_worker_rnk
 WHERE data_rnk = 1
       )
SELECT
        'CW-' || LPAD(rnk::VARCHAR, 6, '0')                                contingent_worker_id
      , t.*
      , NULLIF(LOWER(TRIM(t.first_name             )), '')                 nrm_first_name
      , NULLIF(LOWER(TRIM(t.last_name              )), '')                 nrm_last_name
      , NULLIF(LOWER(TRIM(t.primary_email          )), '')                 nrm_primary_email
      , NULLIF(LOWER(TRIM(t.secondary_email        )), '')                 nrm_secondary_email
      , NULLIF(LOWER(TRIM(t.manager_name           )), '')                 nrm_manager_name
      , NULLIF(LOWER(TRIM(t.manager_email_address  )), '')                 nrm_manager_email_address
      , NULLIF(LOWER(TRIM(t.manager_email          )), '')                 nrm_manager_email
      , l.target_value                                                     nrm_location
     , COALESCE(w1.target_value, w2.target_value, 'Sole Trader Staff')     nrm_worker_type
     , 'Full Time'                                                         nrm_time_type
     , '40'                                                                nrm_hours_per_week                
     , strftime(
         COALESCE(
           TRY_STRPTIME(NULLIF(TRIM(t.deactivation_date), ''), '%Y-%m-%d %H:%M:%S')
         , TRY_STRPTIME(NULLIF(TRIM(t.deactivation_date), ''), '%Y-%m-%d')
         , TRY_STRPTIME(NULLIF(TRIM(t.deactivation_date), ''), '%d-%m-%Y')
         , CURRENT_DATE + INTERVAL '6 MONTH'
         ), '%Y-%m-%d 00:00:00'
       )                                                                   nrm_deactivation_date
  FROM 
       cte_contingent_worker              t
       LEFT OUTER JOIN 
       ref_location_mapping               l
          ON l.source_column             = 'location'
         AND l.source_value              = NULLIF(TRIM(t.location), '')
       LEFT OUTER JOIN
       ref_worker_type_mapping            w1
          ON w1.source_column             = 'user_type'
         AND w1.source_value              = NULLIF(TRIM(t.user_type), '')
       LEFT OUTER JOIN
       ref_worker_type_mapping            w2
          ON w2.source_column             = 'department_1'
         AND w2.source_value              = NULLIF(TRIM(t.department_1), '')
 WHERE 
       l.target_value                     IS NOT NULL
   AND (
       w1.target_value                   != 'EXCLUDE'
    OR w2.target_value                   != 'EXCLUDE'
       )
;
