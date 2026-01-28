SELECT
    p.state,
    p.provider_type,
    d.drug_name,
    d.generic_name,
    SUM(f.sales_amount) AS sales_amount,
    SUM(f.total_claims) AS total_claims
FROM fact_sales f
JOIN dim_provider p ON f.provider_id = p.provider_id
JOIN dim_drug d ON f.drug_id = d.drug_id
WHERE f.sale_year = :sale_year
GROUP BY 
    p.state, 
    p.provider_type, 
    d.drug_name,
    d.generic_name;