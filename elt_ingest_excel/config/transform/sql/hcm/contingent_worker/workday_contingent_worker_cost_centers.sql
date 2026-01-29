DROP TABLE IF EXISTS workday_contingent_worker_cost_centers
;
CREATE TABLE workday_contingent_worker_cost_centers
    AS
  WITH cte_cost_centers
    AS (
SELECT DISTINCT
       TRIM(cost_center)                                cost_center
  FROM src_hcm_contingent_worker
 WHERE cost_center IS NOT NULL
   AND TRIM(cost_center) != ''
       )
SELECT
       TRIM(cost_center)                                cost_center_name
     , NULL                                             cost_center_code
     , NULL                                             include_organization_code_in_name
     , NULL                                             cost_center_id
     , NULL                                             cost_center_hierarchy_1
     , NULL                                             cost_center_hierarchy_2
     , NULL                                             cost_center_hierarchy_3
     , NULL                                             legacy_cost_center_code
  FROM cte_cost_centers
;
