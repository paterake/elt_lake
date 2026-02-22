DROP TABLE IF EXISTS workday_customer_credit
;
CREATE TABLE workday_customer_credit
    AS
SELECT
       c.customer_id                                  customer_id
     , c.nrm_customer_name                            customer_name
     , NULL                                           duns_number
     , NULL                                           exempt_from_dunning
     , TRIM(c.tax_schedule_id)                        tax_code
     , c.nrm_currency_code                            credit_limit_currency
     , CASE
         WHEN UPPER(TRIM(c.credit_limit_type)) = 'UNLIMITED' 
         THEN NULL
         ELSE c.credit_limit_amount
       END                                            credit_limit
     , NULL                                           hierarchy_credit_limit
     , NULL                                           credit_verification_date
     , NULL                                           commercial_credit_score
     , NULL                                           commercial_credit_score_date
     , NULL                                           commercial_credit_score_note
     , NULL                                           composite_risk_score
     , NULL                                           composite_risk_date
     , NULL                                           composite_risk_note
     , NULL                                           customer_satisfaction_score
     , NULL                                           customer_satisfaction_date
     , NULL                                           customer_satisfaction_note
  FROM src_fin_customer                c
;
