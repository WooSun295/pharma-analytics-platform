# Pharma Analytics Platform - CMS Part D ETL

## Overview

This project implements an end-to-end ETL (Extract, Transform, Load) pipeline using publicly available **CMS Medicare Part D Prescriber Data**. The goal is to model large-scale healthcare data into an analytics ready **PostgreSQL data warehouse**, forming the foundation for downstream analytics and visualization.

The pipeline is designed to handle multi-gigabyte CSV files, perform data cleaning and normalization, and load data into a star-schema-style warehouse suitable form pharmaceutical analytics use cases.

## Disclaimer

This project uses publicly available CMS data for educational and portfolio purposes. No patient-level or protected health information (PHI) is included.

## Data Source

- **Dataset**: CMS Medicare Part D Prescriber Public Use File
- **File Used**: MUP_DPR_RY25_P04_V10_DY23_NPIBN.csv
- **Year**: 2023
- **Source**: Centers for Medicare & Medicaid Services (CMS)
- **Link**: [Link to the Data Source] (https://data.cms.gov/provider-summary-by-type-of-service/medicare-part-d-prescribers/medicare-part-d-prescribers-by-provider-and-drug)
  The dataset contains prescription drug utilization and cost information at the prescriber (NPI) and drug level

## Architecture

Raw CMS CSV (3.6 GB)
↓
Chunked Extraction (pandas)
↓
Data Cleaning & Transformation
↓
PostgreSQL Data Warehouse

## Database Schema

The warehouse follows a fact/dimension (star schema) design.

### Dimension Tables

#### dim_drug

- Stores unique drugs
- Keyed by internally generated drug_id
  | Column | Description |
  | ------------ | -------------------------------- |
  | drug_id | Surrogate primary key |
  | drug_name | Brand drug name |
  | generic_name | Generic drug name (if available) |

#### dim_provider

- Stores prescriber-level information
- Keyed by internally generated provider_id
  | Column | Description |
  | -------------- | ---------------------------- |
  | provider_id | Surrogate primary key |
  | prescriber_npi | National Provider Identifier |
  | state | Prescriber state |
  | provider_type | CMS prescriber type |

### Fact Table

#### fact_sales

- Stores prescription cost and utilization metrics
- Grain: provider x drug x year (non-fully aggregated)
  | Column | Description |
  | ------------ | ------------------------- |
  | drug_id | FK → dim_drug |
  | provider_id | FK → dim_provider |
  | sale_year | Reporting year |
  | total_claims | Total prescription claims |
  | sales_amount | Total drug cost |

> Multiple records may exist per provider-drug-year. Aggregation is intentionally performed at query time to preserve data fidelity.

## ETL Pipeline

The ETL process is modularized into 3 components:

### Extract (extract.py)

- Reads the raw CMS CSV using chunked processing
- Prevents memory overload for large datasets
- Configurable chunk size (used: 100,000 rows)

### Transform (transform.py)

- Handles CMS suppression flags (\*)
- Drops rows missing critical fields
- Renames columns to warehouse-friendly names
- Adds derived fields (e.g. sale_year = 2023)
- Ensures Python-native types for database compatibility

### Load (load.py)

- Loads data into PostgreSQL using SQLAlchemy + psycopg2
- Performs:
   - Deduplicated inserts into dimension tables
   - Fact table inserts with foreign key joins
- Enforces referential integrity via foreign keys

### Orchestration (main.py)

- Coordinates extract → transform → load
- Processes all chunks sequentially
- Designed to be re-runnable and fault-tolerant

## Configurations

Environment-specific values are stored in a '.env' file:

CSV_PATH = /path/to/cms_data.csv
DB_URI=postgresql+psycopg2:user:password@localhost5432/pharma_dw

## Data Validation

Post-load checks were performed to ensure data quality:

- Row count sanity checks on fact table (raw = fact_sales = 26,794,878 No Loss)
- Foreign key integrity checks (no orphan records)
- Value sanity checks (no negative costs)
- Duplicate detection and validation
- Distribution spot checks (top drugs by spend)
  Duplicate fact rows were identified and determined to be expected behavior given CMS reporting structure. Aggregation is handled at query time.

## Technology Stack

- Python 3.10+
- pandas
- PostgreSQL
- SQLAlchemy
- psycopg2
- VS Code
- CMS Public Healthcare Data
