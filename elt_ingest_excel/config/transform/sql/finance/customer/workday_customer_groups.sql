DROP TABLE IF EXISTS workday_customer_groups
;
CREATE TABLE workday_customer_groups
    AS
SELECT
       TRIM(c.customer_id)                            customer_id
     , TRIM(c.customer_name)                          customer_name
     , CASE
           WHEN UPPER(SUBSTR(TRIM(c.customer_name), 1, 1)) BETWEEN 'A' AND 'L'
               THEN 'Customers_A_L'
           WHEN UPPER(SUBSTR(TRIM(c.customer_name), 1, 1)) BETWEEN 'M' AND 'Z'
               THEN 'Customers_M_Z'
           ELSE 'Customers_0_9'
       END                                            customer_group
  FROM src_fin_customer                c
 WHERE c.customer_class IS NOT NULL
   AND TRIM(c.customer_class) != ''
;
