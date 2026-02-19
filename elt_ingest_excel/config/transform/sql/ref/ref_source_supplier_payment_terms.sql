DROP TABLE IF EXISTS ref_source_supplier_payment_terms
;
CREATE TABLE ref_source_supplier_payment_terms
    AS
SELECT
       TRIM(source_payment_terms)           source_payment_terms
     , TRIM(workday_payment_terms)          workday_payment_terms
  FROM read_json_auto(
           '/Users/rpatel/Documents/__code/git/emailrak/elt_lake/elt_ingest_excel/config/data/ref_source_supplier_payment_terms.json'
       )
;
