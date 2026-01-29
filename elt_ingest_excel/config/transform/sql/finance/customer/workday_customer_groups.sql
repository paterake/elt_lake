DROP TABLE IF EXISTS workday_customer_groups
;
CREATE TABLE workday_customer_groups
    AS
SELECT
       TRIM(customer_id)                             customer_id
     , TRIM(customer_name)                           customer_name
     , TRIM(customer_class)                          customer_group
  FROM src_fin_customer
 WHERE customer_class IS NOT NULL
   AND TRIM(customer_class) != ''
;
