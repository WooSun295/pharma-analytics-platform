# Pharma Analytics Platform

An end-to-end healthcare analytics platform built using publicly available **CMS Medicare Part D Prescriber data**.

This project demonstrates how large-scale healthcare data can be ingested, modeled, validated, and transformed into analytics-ready datasets, and ultimately visualized through an interactive, cloud-deployed dashboard.

🔗 **Live Demo:** https://www.swlee9867.com

## Project Overview

The platform ingests multi-million-row pharmaceutical claims data, loads it into a PostgreSQL data warehouse using a star schema, and exposes business-critical insights through a Streamlit analytics dashboard hosted on AWS.

Key goals:

- Handle **large-scale healthcare data** efficiently
- Apply **data warehouse design best practices**
- Enable **fast analytical queries** through pre-aggregation
- Deploy a **production-style analytics application** in the cloud

## Architecture

    CMS Part D CSV (26M+ rows)
            ↓
    Python ETL (chunked processing)
            ↓
    PostgreSQL (Star Schema)
            ↓
    Materialized View (Analytics)
            ↓
    Streamlit Dashboard
            ↓
    AWS (Using EC2, RDS, ALB, HTTPS)

## Project Structure

### 1. ETL Pipeline

- Chunked ingestion of multi-gigabyte CMS CSV files
- Data cleaning, normalization, and validation
- Star-schema data warehouse design (facts + dimensions)
- Optimized loading using bulk inserts and staging tables

📁 `etl/` → see `etl/README.md`

### 2. Analytics Layer (in progress)

- SQL-based KPI calculations
- Pre-aggregated materialized views for performance
- State-level and drug-level pharmaceutical spend analysis
- Brand vs Generic spend comparison

📁 `analytics/` → see `analytics/README.md`

## 3. Visualization & Deployment

- Interactive dashboards built with Streamlit
- KPI cards, bar charts, and geographic views
- Hosted on AWS with HTTPS and custom domain
- Load-balanced and secured cloud architecture

📁 analytics/dashboard.py

### 4. Data

- Sample dataset containing 1,500 randomly selected rows from the ETL CMS from PostgreSQL warehouse
- Used for demo mode and development testing
- Full raw CMS dataset intentionally excluded from version control

📁 data/

## Tech Stack

**Data Engineering**

- Python
- pandas
- SQLAlchemy
- PostgreSQL

**Analytics & Visualization**

- SQL
- Streamlit
- Plotly

**Cloud & Deployment**

- AWS EC2
- AWS RDS (PostgreSQL)
- Application Load Balancer
- Route 53 + ACM (HTTPS)

## Data Source

- **CMS Medicare Part D Prescriber Public Use File**
- Reporting Year: 2023
- Public, de-identified healthcare data

## What This Project Demonstrates

- Designing and loading a **large-scale data warehouse**
- Writing **production-oriented ETL pipelines**
- Optimizing analytical performance using **materialized views**
- Building and deploying a **cloud-hosted analytics application**
- Debugging and resolving **real infrastructure constraints** (memory, networking, scaling)

## Author

**Sunwoo Lee**  
Data Analytics / Data Engineering Projects  
🔗 https://www.swlee9867.com
