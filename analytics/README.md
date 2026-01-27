# Pharma Analytics Platform - KPI Dashboard

## Overview

This module implements an interactive analytics dashboard built with **Python and Streamlit**
on top of a PostgreSQL data warehouse populated from **CMS Medicare Part D** data.

The dashboard is designed to surface **pharmaceutical spending, utilization, and market
composition insights** at national and state/regional levels.

## Purpose

The goal of this dashboard is to answer common pharmaceutical analytics questions such as:

- Where is drug spending concentrated geographically?
- Which drugs dominate spend nationally and by state?
- How much spend is driven by **brand vs generic** drugs?
- Which regions account for the highest share of total spend?
- What drugs dominate spend within a specific state or region?

The dashboard is optimized for **exploratory analysis and high-level benchmarking**.

## Key Features

### KPI Summary

- Total Sales
- Total Claims
- Average Cost per Claim
- Top Region by Spend

These KPIs update dynamically based on active filters.

### Top 10 Drugs by Sales

- Bar chart showing the highest-spend drugs
- Dollar values abbreviated (e.g., `$2.345B`, `$123.456M`)
- Supports filtering by state and provider type

### Brand vs Generic Spend Split

- Pie chart showing share of total spend by **Brand vs Generic**
- Tabular breakdown with:
   - Total spend
   - Percent of total
- Classification based on CMS drug naming conventions

### Geographic Spend Analysis

- **US State Choropleth Map** for state-level drug spend
- **Non-US Regions Bar Chart** for territories and special CMS jurisdictions
- Toggle between US-only and region-only views
- Tooltips include formatted spend and percent-of-total context

This design preserves geographic accuracy while ensuring complete regional coverage.

### Regional Analysis (Dropdown-Based)

- Select a state or region from a dropdown menu
- View the **Top 10 drugs** for the selected region
- Each drug displays:
   - Total sales (abbreviated)
   - Percent share of the region’s total spend

This approach provides reliable interaction while maintaining consistent visuals.

## Filters

Available filters include:

- **Year**
- **State / Region**
- **Provider Type**
- **Geographic View** (US States vs Non-US Regions)
- **Demo Mode** (sample CSV vs full database)

All charts and KPIs respond to active filters.

## Demo Mode

The dashboard supports a **Demo Mode** that runs on a lightweight sample CSV
(~1,500 rows) instead of the full PostgreSQL warehouse.

This enables:

- Fast startup
- Easy demos for recruiters
- Reduced resource usage

Demo Mode can be toggled directly from the sidebar. You will need to download the sample data from pharma-analytics-platform/data.

## Tech Stack

- **Python**
- **Streamlit**
- **Pandas**
- **Plotly**
- **PostgreSQL**
- **SQLAlchemy**

## How to Run

From the project root:

```bash
pip install -r requirements.txt
streamlit run analytics/dashboard.py
```

Ensure your `.env` file contains a valid `DB_URI` if Demo Mode is disabled.

## Data Source

- CMS Medicare Part D Prescriber Public Use File
- Public, de-identified healthcare data
- Reporting Year: 2023

## Design Notes

- Aggregation is performed in PostgreSQL for performance
- Pandas is used for lightweight transformations and visualization
- Financial values are formatted at the visualization layer
- Geographic edge cases (territories, special regions) are handled explicitly
- Interactivity favors clarity and reliability over complex event handling
