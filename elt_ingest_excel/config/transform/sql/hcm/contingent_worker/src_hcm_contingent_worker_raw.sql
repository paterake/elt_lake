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
            ORDER BY created_date      DESC NULLS LAST
       ) data_rnk
  FROM cte_contingent_worker_distinct  t
       )
SELECT
       NULLIF(list_aggregate(list_transform(split(lower(TRIM(t.first_name            )), ' '), x -> upper(x[1]) || substr(x, 2)), 'string_agg', ' '), '') nrm_first_name
     , NULLIF(list_aggregate(list_transform(split(lower(TRIM(t.last_name             )), ' '), x -> upper(x[1]) || substr(x, 2)), 'string_agg', ' '), '') nrm_last_name
     , NULLIF(list_aggregate(list_transform(split(lower(TRIM(t.manager_name          )), ' '), x -> upper(x[1]) || substr(x, 2)), 'string_agg', ' '), '') nrm_manager_name
     , NULLIF(list_aggregate(list_transform(split(lower(TRIM(REGEXP_REPLACE(t.title, '[^a-zA-Z0-9 ]', '', 'g'))), ' '), x -> upper(x[1]) || substr(x, 2)), 'string_agg', ' '), '') nrm_title
     , 'Full Time'                                                         nrm_time_type
     , '40'                                                                nrm_hours_per_week                
     , NULLIF(LOWER(TRIM(t.primary_email           )), '')                 nrm_primary_email
     , NULLIF(LOWER(TRIM(t.secondary_email         )), '')                 nrm_secondary_email
     , NULLIF(LOWER(TRIM(t.manager_email_address   )), '')                 nrm_manager_email_address
     , NULLIF(LOWER(TRIM(t.manager_email           )), '')                 nrm_manager_email
     , NULLIF(LOWER(TRIM(t.department              )), '')                 nrm_department
     , NULLIF(LOWER(TRIM(t.department_1            )), '')                 nrm_department_1
     , NULLIF(LOWER(TRIM(t.division                )), '')                 nrm_division
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
     , t.*
  FROM 
       cte_contingent_worker_rnk       t
;
