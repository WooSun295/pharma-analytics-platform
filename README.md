# Pharma Analytics Platform

An end-to-end healthcare analytics platform built using publicly available
**CMS Medicare Part D Prescriber data**.

This project demonstrates how large-scale healthcare data can be ingested,
modeled, validated, and transformed into analytics-ready datasets, and
ultimately visualized through interactive dashboards.

---

## Project Structure

### 1. ETL Pipeline

- Chunked ingestion of multi-gigabyte CMS CSV data
- Data cleaning, normalization, and validation
- Star-schema data warehouse in PostgreSQL

📁 `etl/` → see `etl/README.md`

### 2. Analytics Layer (in progress)

- SQL-based aggregation and KPI development
- Analytical views for pharmaceutical spend and utilization

📁 `analytics/`

### 3. Visualization & Deployment (planned)

- Interactive Streamlit dashboards
- Cloud deployment using AWS

📁 `app/`

### 4. Data

- Contains 1000 random rows from the raw CMS CSV file.

---

## Tech Stack

- Python
- pandas
- PostgreSQL
- SQLAlchemy
- Streamlit
- AWS

---

## Data Source

- **CMS Medicare Part D Prescriber Public Use File**
- Reporting Year: 2023
- Public, de-identified healthcare data

---

## Status

✅ ETL pipeline complete  
🔄 Analytics in progress  
☁️ Streamlit + AWS deployment planned
