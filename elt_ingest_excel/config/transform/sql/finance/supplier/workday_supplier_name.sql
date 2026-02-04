DROP TABLE IF EXISTS workday_supplier_name
;
CREATE TABLE workday_supplier_name 
    AS
SELECT
       s.supplier_id                                  supplier_id
     , s.nrm_vendor_name                             supplier_name
     , TRIM(s.vendor_id)                             reference_id
     , CASE
         WHEN TRIM(s.vendor_class_id) = 'IR35'       THEN 'Professional Services'
         ELSE 'Suppliers'
       END                                         supplier_category
     , s.business_unit                               business_entity_name
     , NULL                                        do_not_reimburse_contingent_worker_expense_reports
     , NULL                                        worktag_only
     , 'Microsoft Dynamics GP'                     integration_system
     , TRIM(s.vendor_id)                             external_entity_id
     , 'Legacy Migration'                          supplier_source
     , 'Migration'                                 supplier_change_source
     , CASE
         WHEN UPPER(TRIM(s.vendor_status)) = 'ACTIVE'  THEN 'Yes'
         ELSE 'No'
       END                                         submit
     , NULL                                        spend_category_or_hierarchy_plus
     , NULL                                        supplier_security_segment
     , NULL                                        create_supplier_from_customer
     , NULL                                        create_supplier_from_financial_institution
     , NULL                                        create_supplier_from_tax_authority
     , NULL                                        create_supplier_from_investor
     , NULLIF(TRIM(s.customer_vendor_id), '')        customer_account_number
     , NULL                                        certificate_of_insurance_date
     , NULL                                        duns_number
     , NULL                                        unique_entity_identifier
  FROM src_fin_supplier s
;
