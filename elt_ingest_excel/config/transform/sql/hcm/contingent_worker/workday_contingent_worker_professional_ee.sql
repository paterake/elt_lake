DROP TABLE IF EXISTS workday_contingent_worker_professional_ee
;
CREATE TABLE workday_contingent_worker_professional_ee
SELECT
       t.contingent_worker_id          worker_id
     , t.first_name                    first_name
     , t.last_name                     last_name
     , t.user_type                     worker_type
     , NULL                            applicant_source_category
     , NULL                            applicant_source_name
     , t.activiation_date              hire_date_contract_start_date
     , NULL                            original_hire_date
     , NULL                            probation_end_date
     , NULL                            continuous_service_date
     , t.user_type                     employee_contingent_worker_type
     , t.deactiviation_date            employment_contract_end_date_fixed_term
     , NULL                            time_type
     , NULL                            pay_rate_type
     , NULL                            job_profile
     , NULL                            job_code
     , NULL                            position_id
     , NULL                            primary_position
     , t.title                         position_name
  FROM cte_cost_centers
;
