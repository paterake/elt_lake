DROP TABLE IF EXISTS workday_contingent_worker_name
;
CREATE TABLE workday_contingent_worker_name
    AS
       t.contingent_worker_id           worker_id
     , t.user_type                      worker_type
     , t.first_name                     first_name
     , t.last_name                      last_name
     , NULL                             title
  FROM src_hcm_contingent_worker
;
