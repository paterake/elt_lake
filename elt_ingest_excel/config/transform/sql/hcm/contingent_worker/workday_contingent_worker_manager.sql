DROP TABLE IF EXISTS workday_contingent_worker_manager
;
CREATE TABLE workday_contingent_worker_manager
    AS
  WITH cte_match
    AS (
SELECT
       t.contingent_worker_id                worker_id
     , NULL                                  position_id
     , m.employee_id                         worker_id_of_direct_manager
     , m.nrm_first_name                      manager_first_name
     , m.nrm_last_name                       manager_last_name
     , t.nrm_first_name                      first_name
     , t.nrm_last_name                       last_name
     , 'Contingent Worker'                   worker_type
     , NULL                                  manager_position_id
     , NULL                                  supervisory_org_code
     , NULL                                  supervisory_org_name
     , NULL                                  supervisory_id
     , NULL                                  staffing_model
     , CASE 
        WHEN m.email_address                 = t.nrm_manager_email_address
         AND m.manager_name                  = t.manager_name
        THEN 1
        WHEN m.email_address                 = t.nrm_manager_email
         AND m.manager_name                  = t.manager_name
        THEN 2
        WHEN m.email_address                 = t.nrm_manager_email_address
        THEN 3
        WHEN m.email_address                 = t.nrm_manager_email
        THEN 4
        WHEN m.manager_name                  = t.nrm_manager_name
        THEN 5
        ELSE 999
       END                                   match_priority
  FROM src_hcm_contingent_worker             t
       LEFT OUTER JOIN 
       src_hcm_contingent_worker_id_mapping  m
          ON m.manager_name                  = t.nrm_manager_name
          OR m.email_address                 = t.nrm_manager_email_address
          OR m.email_address                 = t.nrm_manager_email
       )
     , cte_match_rnk
    AS (
SELECT t.*
     , ROW_NUMBER() OVER (PARTITION BY t.worker_id ORDER BY match_priority) rnk 
       )
SELECT 
       t.worker_id
     , t.position_id
     , t.worker_id_of_direct_manager
     , t.manager_first_name
     , t.manager_last_name
     , t.first_name
     , t.last_name
     , t.worker_type
     , t.manager_position_id
     , t.supervisory_org_code
     , t.supervisory_org_name
     , t.supervisory_id
     , t.staffing_model
  FROM cte_match_rnk                         t
 WHERE t.rnk                                 = 1
;
