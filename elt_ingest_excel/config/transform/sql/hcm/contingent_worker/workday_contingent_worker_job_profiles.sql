DROP TABLE IF EXISTS workday_contingent_worker_job_profiles
;
CREATE TABLE workday_contingent_worker_job_profiles
    AS
  WITH cte_job_profiles
    AS (
SELECT DISTINCT
       TRIM(title)                                      title
  FROM src_hcm_contingent_worker
 WHERE title IS NOT NULL
   AND TRIM(title) != ''
       )
SELECT
       TRIM(title)                                      job_profile
     , NULL                                             job_code
     , NULL                                             include_job_code_in_name
     , NULL                                             public_job
     , NULL                                             job_description
     , NULL                                             grade
     , 'United Kingdom'                                 country
     , 'GBR'                                            country_code
     , NULL                                             exempt_non_exempt
     , NULL                                             pay_rate_type
     , NULL                                             management_level
     , NULL                                             job_levels
     , NULL                                             job_family
     , NULL                                             occupational_series
     , NULL                                             job_family_group
     , NULL                                             job_classification_group
     , NULL                                             job_classification
     , NULL                                             job_classification_id
     , NULL                                             job_classification_group_2
     , NULL                                             job_classification_2
     , NULL                                             job_classification_id_2
     , NULL                                             workers_compensation_code
     , NULL                                             workers_compensation_code_name
     , NULL                                             workers_compensation_code_region
     , NULL                                             job_category
     , NULL                                             company_insider_type
     , NULL                                             critical_job
     , NULL                                             job_profile_summary
     , NULL                                             legacy_job_profiles_name
     , NULL                                             skill
  FROM cte_job_profiles
;
