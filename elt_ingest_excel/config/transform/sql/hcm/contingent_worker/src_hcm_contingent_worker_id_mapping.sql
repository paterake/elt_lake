DROP TABLE IF EXISTS src_hcm_contingent_worker_id_mapping
;
CREATE TABLE src_hcm_contingent_worker_id_mapping
    AS
  WITH cte_worker_id_mapping_raw
    AS (
SELECT DISTINCT
       w.employee_id                                                                   employee_id
     , NULLIF(list_aggregate(list_transform(split(lower(TRIM(w.legal_name_first_name )), ' '), x -> upper(x[1]) || substr(x, 2)), 'string_agg', ' '), '') first_name
     , NULLIF(list_aggregate(list_transform(split(lower(TRIM(w.legal_name_middle_name)), ' '), x -> upper(x[1]) || substr(x, 2)), 'string_agg', ' '), '') middle_name
     , NULLIF(list_aggregate(list_transform(split(lower(TRIM(w.legal_name_last_name  )), ' '), x -> upper(x[1]) || substr(x, 2)), 'string_agg', ' '), '') last_name
     , NULLIF(LOWER(TRIM(TRIM(u.email_address_raw, E'\r\n\t '))), '')                  email_address_raw
  FROM hcm_contingent_worker_id_mapping w
     , UNNEST(
         STRING_SPLIT(REPLACE(REPLACE(w.emails, E'\r\n', E'\n'), E'\r', E'\n'), E'\n')
       ) AS u(email_address_raw)
       )
     , cte_worker_id_mapping
    AS (
SELECT t.*
  FROM cte_worker_id_mapping_raw t
 WHERE t.email_address_raw IS NOT NULL
       )
SELECT t.*
     , NULLIF(TRIM(SPLIT_PART(t.email_address_raw, ' (', 1)), '')                      email_address
     , NULLIF(TRIM(REPLACE(SPLIT_PART(t.email_address_raw, ' (', 2), ')', '')), '')    email_full_name
     , t.first_name || ' ' || t.last_name                                              manager_name
  FROM cte_worker_id_mapping t
 WHERE email_address NOT IN ('test@test.com', 'xx@xx.com')
;
