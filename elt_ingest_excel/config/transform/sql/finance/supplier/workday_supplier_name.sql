DROP TABLE IF EXISTS workday_supplier_name
;
CREATE TABLE workday_supplier_name 
    AS
SELECT
       s.supplier_id                                   supplier_id
     , s.nrm_vendor_name                               supplier_name
     , s.nrm_vendor_id                                 reference_id
     , s.nrm_supplier_category                         supplier_category
     , NULL                                            business_entity_name
     , NULL                                            do_not_reimburse_contingent_worker_expense_reports
     , NULL                                            worktag_only
     , NULL                                            integration_system
     , NULL                                            external_entity_id
     , NULL                                            supplier_source
     , NULL                                            supplier_change_source
     , NULL                                            submit
     , NULL                                            spend_category_or_hierarchy_plus
     , NULL                                            supplier_security_segment
     , NULL                                            create_supplier_from_customer
     , NULL                                            create_supplier_from_financial_institution
     , NULL                                            create_supplier_from_tax_authority
     , NULL                                            create_supplier_from_investor
     , NULL                                            customer_account_number
     , NULL                                            certificate_of_insurance_date
     , NULL                                            duns_number
     , NULL                                            unique_entity_identifier
  FROM src_fin_supplier                               s
;
