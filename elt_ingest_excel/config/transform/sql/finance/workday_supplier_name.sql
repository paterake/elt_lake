DROP TABLE IF EXISTS workday_supplier_name
;
CREATE TABLE workday_supplier_name AS
SELECT 
       TRIM(vendor_id)                             supplier_id
     , TRIM(vendor_name)                           supplier_name
     , TRIM(vendor_id) as                          reference_id
     , CASE 
         WHEN TRIM(vendor_class_id) = 'GENERAL'    THEN 'General Suppliers'
         WHEN TRIM(vendor_class_id) = 'CONSULTING' THEN 'Professional Services'
         WHEN TRIM(vendor_class_id) = 'IT'         THEN 'Technology Suppliers'
         WHEN TRIM(vendor_class_id) = 'FACILITIES' THEN 'Facilities & Maintenance'
         WHEN TRIM(vendor_class_id) = 'MARKETING'  THEN 'Marketing Services'
         -- Add more mappings as needed
         ELSE 'General Suppliers'
       END                                         supplier_category
     , TRIM(vendor_name)                           business_entity_name
     , FALSE                                       do_not_reimburse_contingent_worker_expense_reports
     , FALSE                                       worktag_only
     , 'Microsoft Dynamics GP'                     integration_system
     , TRIM(vendor_id)                             external_entity_id
     , 'Legacy Migration'                          supplier_source
     , 'Migration'                                 supplier_change_source
     , TRUE                                        submit
     , NULL                                        spend_category_or_hierarchy_plus
     , NULL                                        supplier_security_segment
     , FALSE                                       create_supplier_from_customer
     , FALSE                                       create_supplier_from_financial_institution
     , FALSE                                       create_supplier_from_tax_authority
     , FALSE                                       create_supplier_from_investor
     , NULLIF(TRIM(customer_vendor_id), '')        customer_account_number
     , NULL::DATE                                  certificate_of_insurance_date
     , NULL                                        duns_number
     , NULL                                        unique_entity_identifier
  FROM src_fin_supplier
;
