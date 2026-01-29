DROP TABLE IF EXISTS workday_contingent_worker_companies
;
CREATE TABLE workday_contingent_worker_companies
    AS
  WITH cte_companies
    AS (
SELECT DISTINCT
       TRIM(organization)                               organization
  FROM src_hcm_contingent_worker
 WHERE organization IS NOT NULL
   AND TRIM(organization) != ''
       )
SELECT
       TRIM(organization)                               company_name
     , 'GBR'                                            country
     , 'GBR'                                            country_code
     , 'GBP'                                            currency_code
     , NULL                                             region
     , NULL                                             subregion
     , NULL                                             city
     , NULL                                             city_subdivision
     , NULL                                             address_line_1
     , NULL                                             address_line_2
     , NULL                                             address_line_3
     , NULL                                             address_line_4
     , NULL                                             postal_code
     , NULL                                             company_tax_id
     , NULL                                             company_tax_id_type
     , NULL                                             tax_id_type_reference_id
     , NULL                                             company_tax_id_2
     , NULL                                             company_tax_id_type_2
     , NULL                                             tax_id_type_2_reference_id
     , NULL                                             company_code
     , NULL                                             include_company_code_in_name
     , NULL                                             company_id
     , NULL                                             industry_code
     , NULL                                             industry_code_type
     , NULL                                             company_hierarchy_1
     , NULL                                             company_hierarchy_2
     , NULL                                             company_hierarchy_3
  FROM cte_companies
;
