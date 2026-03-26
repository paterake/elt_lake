-- Ensure all entries have a primry defined
SELECT * FROM workday_supplier_email WHERE supplier_id NOT IN (SELECT supplier_id FROM workday_supplier_email WHERE primary_flag = 'Yes');

-- Ensure all entries have a primry defined
SELECT * FROM workday_supplier_phone WHERE supplier_id NOT IN (SELECT supplier_id FROM workday_supplier_phone WHERE primary_flag = 'Yes');