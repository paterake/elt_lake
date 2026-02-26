DROP TABLE IF EXISTS src_hcm_contingent_worker_raw
;
CREATE TABLE src_hcm_contingent_worker_raw
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
       'CW-' || LPAD(rnk::VARCHAR, 6, '0')                                 contingent_worker_id
     , t.*
     , strftime(
          COALESCE(
          TRY_STRPTIME(NULLIF(TRIM(t.created_date ), ''), '%Y-%m-%dT%H:%M:%S.%fZ')
        , TRY_STRPTIME(NULLIF(TRIM(t.created_date ), ''), '%Y-%m-%d %H:%M:%S')
        , TRY_STRPTIME(NULLIF(TRIM(t.created_date ), ''), '%Y-%m-%d')
        , TRY_STRPTIME(NULLIF(TRIM(t.created_date ), ''), '%d-%m-%Y')
        ), '%Y-%m-%d 00:00:00'
       )                                                                   nrm_created_date
     , strftime(
          COALESCE(
          TRY_STRPTIME(NULLIF(TRIM(t.activated_date ), ''), '%Y-%m-%dT%H:%M:%S.%fZ')
        , TRY_STRPTIME(NULLIF(TRIM(t.activated_date ), ''), '%Y-%m-%d %H:%M:%S')
        , TRY_STRPTIME(NULLIF(TRIM(t.activated_date ), ''), '%Y-%m-%d')
        , TRY_STRPTIME(NULLIF(TRIM(t.activated_date ), ''), '%d-%m-%Y')
        ), '%Y-%m-%d 00:00:00'
       )                                                                   nrm_activated_date
     , strftime(
          COALESCE(
          TRY_STRPTIME(NULLIF(TRIM(t.last_login_date ), ''), '%Y-%m-%dT%H:%M:%S.%fZ')
        , TRY_STRPTIME(NULLIF(TRIM(t.last_login_date ), ''), '%Y-%m-%d %H:%M:%S')
        , TRY_STRPTIME(NULLIF(TRIM(t.last_login_date ), ''), '%Y-%m-%d')
        , TRY_STRPTIME(NULLIF(TRIM(t.last_login_date ), ''), '%d-%m-%Y')
        ), '%Y-%m-%d 00:00:00'
       )                                                                   nrm_last_login_date
     , strftime(
         COALESCE(
           TRY_STRPTIME(NULLIF(TRIM(t.activation_date), ''), '%Y-%m-%dT%H:%M:%S.%fZ')
         , TRY_STRPTIME(NULLIF(TRIM(t.activation_date), ''), '%Y-%m-%d %H:%M:%S')
         , TRY_STRPTIME(NULLIF(TRIM(t.activation_date), ''), '%Y-%m-%d')
         , TRY_STRPTIME(NULLIF(TRIM(t.activation_date), ''), '%d-%m-%Y')
         ), '%Y-%m-%d 00:00:00'
       )                                                                   nrm_activation_date
     , strftime(
         COALESCE(
           TRY_STRPTIME(NULLIF(TRIM(t.deactivation_date), ''), '%Y-%m-%dT%H:%M:%S.%fZ')
         , TRY_STRPTIME(NULLIF(TRIM(t.deactivation_date), ''), '%Y-%m-%d %H:%M:%S')
         , TRY_STRPTIME(NULLIF(TRIM(t.deactivation_date), ''), '%Y-%m-%d')
         , TRY_STRPTIME(NULLIF(TRIM(t.deactivation_date), ''), '%d-%m-%Y')
         , CURRENT_DATE + INTERVAL '6 MONTH'
         ), '%Y-%m-%d 00:00:00'
       )                                                                   nrm_deactivation_date
  FROM 
       cte_contingent_worker              t
;
