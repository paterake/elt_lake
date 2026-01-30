DROP TABLE IF EXISTS workday_contingent_worker_email
;
CREATE TABLE workday_contingent_worker_email
    AS
SELECT
       t.contingent_worker_id                           worker_id
     , TRIM(t.first_name)                               first_name
     , TRIM(t.last_name)                                last_name
     , 'Contingent Worker'                              worker_type
     , 'Work'                                           email_type
     , TRIM(t.primary_email)                            email_address
     , 'Y'                                              is_public
     , 'Y'                                              is_primary
  FROM src_hcm_contingent_worker t
 WHERE t.primary_email IS NOT NULL
   AND TRIM(t.primary_email) != ''
;
