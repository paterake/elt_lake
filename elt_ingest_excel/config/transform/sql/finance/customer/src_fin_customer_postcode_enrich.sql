SELECT 
      c.nrm_customer_number
    , c.nrm_customer_name
    , c.nrm_postal_code    
    -- 1. Region (Broadest)
    , p.region                                      AS geo_region    
    -- 2. County (if available, otherwise fallback to District/Region)
    , cnty.name                                     AS geo_county_name
    , COALESCE(cnty.name, p.region)                 AS geo_county_or_region    
    -- 3. District / City (Best proxy for City/Town in this dataset)
    , dist.name                                     AS geo_district_city_name    
    -- 4. Ward (Most granular)
    , ward.name                                     AS geo_ward_name    
    -- 5. Country (England, Scotland, etc.)
    , p.country                                     AS geo_country
    -- 6. Coordinates (now stored as VARCHAR, cast to DOUBLE if needed)
    , p.latitude
    , p.longitude
FROM src_fin_customer_raw c  -- Or your main customer table
LEFT JOIN postcodes p 
    -- Join on compact postcode (no spaces) to handle formatting differences
    ON UPPER(REPLACE(c.nrm_postal_code, ' ', '')) = p.pc_compact 
-- Map IDs to Names
LEFT JOIN counties cnty 
    ON p.admin_county_id = cnty.code
LEFT JOIN districts dist 
    ON p.admin_district_id = dist.code
LEFT JOIN wards ward 
    ON p.admin_ward_id = ward.code
WHERE c.nrm_postal_code IS NOT NULL;
