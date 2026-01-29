SELECT
  state,
  provider_type,
  drug_name,
  generic_name,
  sales_amount,
  total_claims
FROM mv_sales_agg_y2023
WHERE sale_year = %(sale_year)s;