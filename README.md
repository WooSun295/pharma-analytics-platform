# Pharma Analytics Platform

An end-to-end healthcare analytics platform built using publicly available
**CMS Medicare Part D Prescriber data**.

This project demonstrates how large-scale healthcare data can be ingested,
modeled, validated, and transformed into analytics-ready datasets, and
ultimately visualized through interactive dashboards.

## Project Overview

The platform is structured as a multi-layer analytics system:

1. **ETL pipeline** for ingesting and modeling raw CMS data
2. **Analytics layer** for KPI computation and exploratory analysis
3. **Visualization layer** for interactive dashboards and insights

Each layer is designed to reflect real-world data engineering and analytics
workflows used in healthcare and pharmaceutical analytics.

## Project Structure

### 1. ETL Pipeline

- Chunked ingestion of multi-gigabyte CMS CSV files
- Data cleaning, normalization, and suppression handling
- Star-schema data warehouse design
- PostgreSQL-based fact and dimension tables
- Validation checks to ensure data integrity

📁 `etl/` → see `etl/README.md`

### 2. Analytics Layer (in progress)

- SQL-based aggregation for performance and scalability
- KPI development for pharmaceutical spend and utilization
- Geographic analysis at state and regional levels
- Brand vs Generic spend analysis
- Dropdown-based regional analysis for Top 10 drugs
- Demo mode using a lightweight sample dataset

📁 `analytics/` → see `analytics/README.md`

## 3. Visualization & Deployment

- Interactive dashboards built with Streamlit
- KPI cards, bar charts, maps, and summary tables
- Designed for exploratory analysis and benchmarking
- Cloud deployment planned using AWS

📁 analytics/dashboard.py

### 4. Data

- Sample dataset containing 1,000 randomly selected rows from the original CMS CSV file
- Used for demo mode and development testing
- Full raw CMS dataset intentionally excluded from version control

📁 data/

## Tech Stack

- Python
- pandas
- PostgreSQL
- SQLAlchemy
- Streamlit
- Plotly
- AWS

## Data Source

- **CMS Medicare Part D Prescriber Public Use File**
- Reporting Year: 2023
- Public, de-identified healthcare data
