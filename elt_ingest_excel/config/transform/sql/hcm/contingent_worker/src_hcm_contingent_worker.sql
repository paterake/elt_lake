DROP TABLE IF EXISTS src_hcm_contingent_worker
;
CREATE TABLE src_hcm_contingent_worker
    AS
SELECT
       t.*
     , NULLIF(list_aggregate(list_transform(split(lower(TRIM(t.first_name            )), ' '), x -> upper(x[1]) || substr(x, 2)), 'string_agg', ' '), '') nrm_first_name
     , NULLIF(list_aggregate(list_transform(split(lower(TRIM(t.last_name             )), ' '), x -> upper(x[1]) || substr(x, 2)), 'string_agg', ' '), '') nrm_last_name
     , NULLIF(LOWER(TRIM(t.primary_email           )), '')                 nrm_primary_email
     , NULLIF(LOWER(TRIM(t.secondary_email         )), '')                 nrm_secondary_email
     , NULLIF(list_aggregate(list_transform(split(lower(TRIM(t.manager_name          )), ' '), x -> upper(x[1]) || substr(x, 2)), 'string_agg', ' '), '') nrm_manager_name
     , NULLIF(LOWER(TRIM(t.manager_email_address   )), '')                 nrm_manager_email_address
     , NULLIF(LOWER(TRIM(t.manager_email           )), '')                 nrm_manager_email
     , l.target_value                                                      nrm_location
     , NULLIF(TRIM(REGEXP_REPLACE(t.title, '[^a-zA-Z0-9 ]', '', 'g')), '') nrm_title
     , COALESCE(rw.mapped_value, 'Sole Trader Staff')                      nrm_worker_type
     , 'Full Time'                                                         nrm_time_type
     , '40'                                                                nrm_hours_per_week                
  FROM 
       src_hcm_contingent_worker_raw      t
       LEFT OUTER JOIN 
       ref_location_mapping               l
          ON l.source_column              = 'location'
         AND UPPER(l.source_value)        = UPPER(COALESCE(NULLIF(TRIM(t.location), ''), 'Wembley Stadium'))
       LEFT OUTER JOIN
       ref_worker_type_mapping            rw
          ON UPPER(rw.user_type)          = UPPER(COALESCE(NULLIF(TRIM(t.user_type)   , ''), 'NULL'))
         AND UPPER(rw.department_1)       = UPPER(COALESCE(NULLIF(TRIM(t.department_1), ''), 'NULL'))
 WHERE 
       1 = 1
   AND COALESCE(NULLIF(UPPER(TRIM(t.location))    , ''), 'NULL') NOT IN ('COUNTY', 'SERVICE_ACCOUNT', 'SERVICE ACCOUNT')
   AND COALESCE(NULLIF(UPPER(TRIM(t.department_1)), ''), 'NULL') NOT IN ('COUNTY', 'SERVICE_ACCOUNT', 'SERVICE ACCOUNT')
   AND COALESCE(NULLIF(UPPER(TRIM(t.user_type))   , ''), 'NULL') NOT IN ('COUNTY', 'SERVICE_ACCOUNT', 'SERVICE ACCOUNT')
;
