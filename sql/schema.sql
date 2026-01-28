CREATE TABLE IF NOT EXISTS dim_drug (
    drug_id SERIAL PRIMARY KEY,
    drug_name TEXT UNIQUE,
    generic_name TEXT
);

CREATE TABLE IF NOT EXISTS dim_provider (
    provider_id SERIAL PRIMARY KEY,
    prescriber_npi TEXT UNIQUE,
    state TEXT,
    provider_type TEXT
);

CREATE TABLE IF NOT EXISTS fact_sales (
    sale_id SERIAL PRIMARY KEY,
    drug_id INTEGER REFERENCES dim_drug(drug_id),
    provider_id INTEGER REFERENCES dim_provider(provider_id),
    sale_year INTEGER,
    total_claims INTEGER,
    sales_amount NUMERIC
);
