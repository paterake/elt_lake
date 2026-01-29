DROP TABLE IF EXISTS workday_contingent_worker_professional_ee
;
CREATE TABLE workday_contingent_worker_professional_ee
    AS
SELECT
       t.contingent_worker_id                           worker_id
     , TRIM(t.first_name)                               first_name
     , TRIM(t.last_name)                                last_name
     , 'Contingent Worker'                              worker_type
     , NULL                                             applicant_source_category
     , NULL                                             applicant_source_name
     , t.activation_date                                hire_date_contract_start_date
     , NULL                                             original_hire_date
     , NULL                                             probation_end_date
     , NULL                                             continuous_service_date
     , NULL                                             seniority_date
     , TRIM(t.user_type)                                employee_contingent_worker_type
     , t.deactivation_date                              employment_contract_end_date_fixed_term
     , NULL                                             time_type
     , NULL                                             pay_rate_type
     , NULL                                             job_profile
     , NULL                                             job_code
     , NULL                                             position_id
     , NULL                                             primary_position
     , TRIM(t.title)                                    position_name
     , t.activation_date                                position_start_date
     , TRIM(t.title)                                    business_title
     , TRIM(t.location)                                 location_name
     , NULL                                             work_space
     , NULL                                             scheduled_weekly_hours
     , NULL                                             default_weekly_hours
     , NULL                                             fte
     , TRIM(t.organization)                             company_org_name
     , NULL                                             company_code
     , NULL                                             establishment
     , TRIM(t.cost_center)                              cost_center_code
     , NULL                                             fund
     , NULL                                             work_shift_country
     , NULL                                             work_shift
     , NULL                                             work_shift_id
     , NULL                                             distance_home_work
     , TRIM(t.department_1)                             contingent_worker_agency
     , NULL                                             remote_ee
     , NULL                                             custom_org_1
     , NULL                                             custom_org_2
     , NULL                                             custom_org_3
     , NULL                                             annual_work_period
     , NULL                                             disbursement_plan_period
     , NULL                                             contract_pay_rate
     , NULL                                             contract_pay_currency
     , NULL                                             contract_pay_frequency
     , NULL                                             working_time_frequency
     , NULL                                             working_time_unit
     , NULL                                             working_time_value
     , NULL                                             working_fte
     , NULL                                             paid_fte
     , NULL                                             region_assignment
     , NULL                                             employment_system
     , NULL                                             time_type_subtype
     , NULL                                             appointment_type
     , NULL                                             employee_tenure
     , NULL                                             annuitant_indicator
     , NULL                                             job_classification
     , NULL                                             hire_employee_1
     , NULL                                             hire_employee_2
     , NULL                                             contract_contingent
     , NULL                                             additional_job
  FROM src_hcm_contingent_worker t
;
