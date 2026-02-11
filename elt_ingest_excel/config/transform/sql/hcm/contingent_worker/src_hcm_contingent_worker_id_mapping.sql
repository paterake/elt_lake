DROP TABLE IF EXISTS src_hcm_contingent_worker_id_mapping
;
CREATE TABLE src_hcm_contingent_worker_id_mapping
    AS
  WITH cte_worker_id_mapping_raw
    AS (
SELECT DISTINCT
       w.employee_id                                                 employee_id
     , LOWER(TRIM(w.legal_name_first_name))                          first_name
     , LOWER(TRIM(w.legal_name_middle_name))                         middle_name
     , LOWER(TRIM(w.legal_name_last_name))                           last_name
     , NULLIF(LOWER(TRIM(TRIM(u.email_address, E'\r\n\t '))), '')    email_address
  FROM hcm_contingent_worker_id_mapping w
     , UNNEST(
         STRING_SPLIT(REPLACE(REPLACE(w.emails, E'\r\n', E'\n'), E'\r', E'\n'), E'\n')
       ) AS u(email_address)
       )
     , cte_worker_id_mapping
    AS (
SELECT t.*
  FROM cte_worker_id_mapping_raw t
       )
SELECT *
  FROM cte_worker_id_mapping
;
