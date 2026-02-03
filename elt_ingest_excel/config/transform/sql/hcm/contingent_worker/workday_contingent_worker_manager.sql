DROP TABLE IF EXISTS workday_contingent_worker_manager
;
CREATE TABLE workday_contingent_worker_manager
    AS
SELECT
       t.contingent_worker_id                            worker_id
     , NULL                                              position_id
     , m.worker_id                                       worker_id_of_direct_manager
     , TRIM(m.first_name)                                manager_first_name
     , TRIM(m.last_name)                                 manager_last_name
     , TRIM(t.first_name)                                first_name
     , TRIM(t.last_name)                                 last_name
     , 'Contingent Worker'                               worker_type
     , NULL                                              manager_position_id
     , NULL                                              supervisory_org_code
     , NULL                                              supervisory_org_name
     , NULL                                              supervisory_id
     , NULL                                              staffing_model
  FROM src_hcm_contingent_worker          t
       LEFT OUTER JOIN 
       hcm_contingent_worker_id_mapping   m
          ON LOWER(TRIM(m.first_name)) || ' ' || LOWER(TRIM(m.last_name))
             = LOWER(TRIM(t.manager_name))
;
