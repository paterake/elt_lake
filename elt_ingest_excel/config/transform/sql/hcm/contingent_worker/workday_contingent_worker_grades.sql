DROP TABLE IF EXISTS workday_contingent_worker_grades
;
CREATE TABLE workday_contingent_worker_grades
    AS
SELECT
       NULL                                             grade_name
     , NULL                                             grade_description
     , NULL                                             other_eligibility
     , NULL                                             minimum
     , NULL                                             midpoint
     , NULL                                             maximum
     , NULL                                             frequency
     , NULL                                             country
     , NULL                                             country_code
     , NULL                                             currency_code
     , NULL                                             grade_reference_id
     , NULL                                             compensation_package
     , NULL                                             assign_1st_step_during_compensation_proposal
     , NULL                                             allow_override
     , NULL                                             compensation_step_plan
 WHERE 1 = 0
;
