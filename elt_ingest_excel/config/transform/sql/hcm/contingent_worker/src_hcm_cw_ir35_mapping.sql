WITH c2 as(SELECT lower(consultant_first_name) first_name, lower(consultant_last_name) last_name, e_mail, division, team, manager_admin FROM hcm_ir36_check)
   , c1 as(SELECT nrm_first_name, nrm_last_name, nrm_primary_email, nrm_secondary_email, nrm_manager_name, nrm_manager_email_address, nrm_manager_email FROM src_hcm_contingent_worker)
SELECT c1.*
     , t1.first_name, t1.last_name
     , t2.e_mail
     , t3.e_mail
     , t4.manager_admin
  FROM c1
       LEFT OUTER JOIN 
       c2 t1
         ON t1.first_name = c1.nrm_first_name
        AND t1.last_name  = c1.nrm_last_name
       LEFT OUTER JOIN 
       c2 t2
         ON t2.e_mail = c1.nrm_primary_email
       LEFT OUTER JOIN 
       c2 t3
         ON t3.e_mail = c1.nrm_secondary_email
       LEFT OUTER JOIN 
       c2 t4
         ON t4.manager_admin LIKE '%'||nrm_manager_name||'%'
WHERE t1.first_name IS NOT NULL 
   OR t2.e_mail IS NOT NULL
   OR t3.e_mail IS NOT NULL
   OR t4.manager_admin IS NOT null
;