CREATE TABLE dim_drug (
  drug_id SERIAL PRIMARY KEY,
  drug_name TEXT UNIQUE,
  generic_name TEXT
);

CREATE TABLE dim_provider (
  provider_id SERIAL PRIMARY KEY,
  prescriber_npi TEXT UNIQUE,
  state TEXT,
  provider_type TEXT
);

CREATE TABLE fact_sales (
  sale_id SERIAL PRIMARY KEY,
  drug_id INT REFERENCES dim_drug(drug_id),
  provider_id INT REFERENCES dim_provider(provider_id),
  sale_year INT,
  total_claims INT,
  sales_amount NUMERIC
);
