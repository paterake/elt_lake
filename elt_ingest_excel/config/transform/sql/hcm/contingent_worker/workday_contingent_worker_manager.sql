DROP TABLE IF EXISTS workday_contingent_worker_manager
;
CREATE TABLE workday_contingent_worker_manager
    AS
  WITH cte_manager_default
    AS (
SELECT m.employee_id                            employee_id
     , m.first_name                             first_name
     , m.last_name                              last_name
  FROM src_hcm_contingent_worker_id_mapping     m
 WHERE LOWER(m.first_name)                      = LOWER('samuel')
   AND LOWER(m.last_name)                       = LOWER('vickers')
       )
     , cte_match
    AS (
SELECT
       t.contingent_worker_id                   worker_id
     , NULL                                     position_id
     , COALESCE(m.employee_id, md.employee_id)  worker_id_of_direct_manager
     , COALESCE(m.first_name , md.first_name )  manager_first_name
     , COALESCE(m.last_name  , md.last_name  )  manager_last_name
     , t.nrm_first_name                         first_name
     , t.nrm_last_name                          last_name
     , 'Contingent Worker'                      worker_type
     , NULL                                     manager_position_id
     , NULL                                     supervisory_org_code
     , NULL                                     supervisory_org_name
     , NULL                                     supervisory_id
     , NULL                                     staffing_model
     , CASE 
        WHEN LOWER(m.email_address)             = LOWER(t.nrm_manager_email_address)
         AND LOWER(m.manager_name)              = LOWER(t.nrm_manager_name)
        THEN 1
        WHEN LOWER(m.email_address)             = LOWER(t.nrm_manager_email)
         AND LOWER(m.manager_name)              = LOWER(t.nrm_manager_name)
        THEN 2
        WHEN LOWER(m.email_address)             = LOWER(t.nrm_manager_email_address)
        THEN 3
        WHEN LOWER(m.email_address)             = LOWER(t.nrm_manager_email)
        THEN 4
        WHEN LOWER(m.manager_name)              = LOWER(t.nrm_manager_name)
        THEN 5
        ELSE 999
       END                                      match_priority
  FROM src_hcm_contingent_worker                t
       CROSS JOIN 
       cte_manager_default                      md
       LEFT OUTER JOIN 
       src_hcm_contingent_worker_id_mapping     m
          ON LOWER(m.manager_name)              = LOWER(t.nrm_manager_name)
          OR LOWER(m.email_address)             = LOWER(t.nrm_manager_email_address)
          OR LOWER(m.email_address)             = LOWER(t.nrm_manager_email)
       )
     , cte_match_rnk
    AS (
SELECT t.*
     , ROW_NUMBER() OVER (PARTITION BY t.worker_id ORDER BY match_priority) rnk 
  FROM cte_match                                t
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
  FROM cte_match_rnk                            t
 WHERE t.rnk                                    = 1
   AND t.worker_id_of_direct_manager            IS NOT NULL
;
