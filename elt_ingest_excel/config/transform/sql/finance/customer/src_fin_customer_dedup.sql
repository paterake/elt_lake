
INSTALL splink_udfs FROM community;
LOAD splink_udfs;

DROP TABLE IF EXISTS src_fin_customer_dedup;

CREATE TABLE src_fin_customer_dedup AS
  WITH cte_customer_score
    AS (
SELECT 
       (
         (CASE WHEN t.nrm_payment_terms_id         IS NOT NULL THEN 100 ELSE 0 END) 
       + (CASE WHEN t.nrm_tax_schedule_id          IS NOT NULL AND t.nrm_tax_schedule_id = 'SS20'  THEN 90 ELSE 0 END) 
       + (CASE WHEN t.nrm_tax_schedule_id          IS NOT NULL AND t.nrm_tax_schedule_id <> 'SS20' THEN 80 ELSE 0 END) 
       + (CASE WHEN t.nrm_tax_registration_number  IS NOT NULL THEN 70 ELSE 0 END) 
       + (CASE WHEN t.nrm_region                   IS NOT NULL THEN 60 ELSE 0 END)
       + (CASE WHEN t.nrm_postal_code              IS NOT NULL THEN 50 ELSE 0 END) 
       + (CASE WHEN t.nrm_address_line_1           IS NOT NULL THEN 40 ELSE 0 END) 
       + (CASE WHEN t.nrm_address_line_2           IS NOT NULL THEN 30 ELSE 0 END) 
       + (CASE WHEN t.nrm_address_line_3           IS NOT NULL THEN 20 ELSE 0 END) 
       + (CASE WHEN t.nrm_city                     IS NOT NULL THEN 10 ELSE 0 END) 
       )                               score
     , t.*
  FROM src_fin_customer_raw            t
       )
     , cte_agg
    AS (
SELECT t.nrm_customer_name
     , ARRAY_AGG(DISTINCT(ARRAY_VALUE( t.nrm_address_line_1
                                     , t.nrm_address_line_2
                                     , t.nrm_address_line_3
                                     , t.nrm_address_line_4
                                     , t.nrm_region
                                     , t.nrm_city
                                     , t.nrm_country_name
                                     , t.nrm_country_code
                                     , t.nrm_postal_code
                                     , t.address_code
                                     )))                             nrm_array_customer_address
     , STRING_AGG(DISTINCT(ARRAY_VALUE(t.phone_1)), ';')             nrm_agg_phone_1
     , STRING_AGG(DISTINCT(ARRAY_VALUE(t.phone_2)), ';')             nrm_agg_phone_2
     , STRING_AGG(DISTINCT(ARRAY_VALUE(t.phone_3)), ';')             nrm_agg_phone_3
     , STRING_AGG(DISTINCT(ARRAY_VALUE(t.fax    )), ';')             nrm_agg_fax
     , STRING_AGG(DISTINCT(ARRAY_VALUE(t.email_to_address )), ';')   nrm_agg_email_to_address
     , STRING_AGG(DISTINCT(ARRAY_VALUE(t.email_cc_address )), ';')   nrm_agg_email_cc_address
     , STRING_AGG(DISTINCT(ARRAY_VALUE(t.email_bcc_address)), ';')   nrm_agg_email_bcc_address
  FROM cte_customer_score              t
 GROUP BY t.nrm_customer_name
       )
SELECT 
       ROW_NUMBER() OVER(PARTITION BY t.nrm_customer_name ORDER BY t.score DESC) rnk_score
     , COUNT()      OVER(PARTITION BY t.nrm_customer_name)                       cnt_customer_name
     , a.nrm_array_customer_address
     , a.nrm_agg_phone_1
     , a.nrm_agg_phone_2
     , a.nrm_agg_phone_3
     , a.nrm_agg_fax
     , a.nrm_agg_email_to_address
     , a.nrm_agg_email_cc_address
     , a.nrm_agg_email_bcc_address
     , t.*
  FROM cte_customer_score              t
       INNER JOIN 
       cte_agg                         a
          ON a.nrm_customer_name       = t.nrm_customer_name
;
