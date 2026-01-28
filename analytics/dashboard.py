import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import plotly.express as px
from streamlit_plotly_events import plotly_events
from pathlib import Path

# Load environment variables
load_dotenv()
DB_URI = os.getenv("DB_URI")

# Check
if not DB_URI:
    raise ValueError("Missing environment variables: CSV_PATH or DB_URI")

# Connect to DB
engine = create_engine(DB_URI)

US_STATES = [
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA",
    "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
    "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
    "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC"
]

def load_sql_query(path: str) -> str:
    return Path(path).read_text()

@st.cache_data(ttl=600)
def load_data(demo_mode: bool, selected_year: int):
    if demo_mode:
        df = pd.read_csv("data/SAMPLE_ETL_CMS_1500.csv")
        return df[df["sale_year"] == selected_year]

    # Production mode → aggregated SQL ONLY
    sql = load_sql_query("sql/analytics_query.sql")

    return pd.read_sql(
        sql,
        engine,
        params={"sale_year": selected_year}
    )

def format_currency_abbrev(value):
    if value >= 1_000_000_000:
        return f"${value/1_000_000_000:.3f}B"
    elif value >= 1_000_000:
        return f"${value/1_000_000:.3f}M"
    elif value >= 1_000:
        return f"${value/1_000:.3f}k"
    else:
        return f"${value:,.2f}"

# ------------------------------
# Sidebar filters
# ------------------------------
st.sidebar.header("Filters")

# Demo Mode using sample data
demo_mode = st.sidebar.toggle(
    "Demo Mode (Sample Data)",
    value=True
)

# Year Filter
selected_year = st.sidebar.selectbox(
    "Select Year",
    options=[2023],  # Extend later if more years are loaded
    index=0
)

# Region Filter for Map
region_view = st.sidebar.radio(
    "Geographic View",
    options=["US States Map", "Non-US Regions Chart"],
    index=0
)

df = load_data(demo_mode, selected_year)

# Unique states from the loaded DataFrame
state_options = sorted(df["state"].unique())
selected_state = st.sidebar.multiselect(
    "Select State(s)",
    options=state_options,
    default=state_options
)

# Unique provider types from the DataFrame
provider_options = sorted(df["provider_type"].unique())
selected_providers = st.sidebar.multiselect(
    "Select Provider Type(s)",
    options=provider_options,
    default=provider_options
)

filtered_df = df[
    (df["state"].isin(selected_state)) &
    (df["provider_type"].isin(selected_providers))
]

if "selected_region" not in st.session_state:
    st.session_state["selected_region"] = None

# Streamlit Header
st.set_page_config(page_title="Pharma KPI Dashboard", layout="wide")
st.title("Pharma KPI Dashboard")
st.markdown("Interactive insights from CMS Medicare Part D data")
if demo_mode:
    st.info("Demo Mode enabled — using 1,500-row sample dataset")
else:
    st.success("Connected to PostgreSQL warehouse")

# ------------------------------
# Top 10 Drugs by State/Region
# ------------------------------
drug_state_df = (
    filtered_df.groupby(["state", "drug_name"], as_index=False)
      .agg(total_sales=("sales_amount", "sum"))
)

# Total sales per state
state_totals = (
    drug_state_df.groupby("state", as_index=False)
    .agg(state_total=("total_sales", "sum"))
)

drug_state_df = drug_state_df.merge(state_totals, on="state")

drug_state_df["pct_of_state"] = (
    drug_state_df["total_sales"] / drug_state_df["state_total"] * 100
)

# Rank drugs per state
drug_state_df["rank"] = (
    drug_state_df.groupby("state")["total_sales"]
    .rank(method="first", ascending=False)
)

top10_by_state = drug_state_df[
    drug_state_df["rank"] <= 10
].copy()

# ------------------------------
# Top 10 Drugs by Sales
# ------------------------------
top_drugs_df = (
    filtered_df
    .groupby("drug_name", as_index=False)
    .agg(total_sales=("sales_amount", "sum"))
    .sort_values("total_sales", ascending=False)
    .head(10)
)

top_drugs_df["sales_label"] = top_drugs_df["total_sales"].apply(
    format_currency_abbrev
)

# ------------------------------
# Sidebar filters
# ------------------------------
tmp = filtered_df.copy()

tmp["drug_name_norm"] = tmp["drug_name"].astype(str).str.strip().str.lower()
tmp["generic_name_norm"] = tmp["generic_name"].astype(str).str.strip().str.lower()

# Generic if brand name == generic name (common rule for CMS Part D)
tmp["drug_type"] = tmp.apply(
    lambda r: "Generic"
    if pd.notna(r["generic_name"]) and r["generic_name_norm"] != "nan" and r["drug_name_norm"] == r["generic_name_norm"]
    else "Brand",
    axis=1
)

bg_df = (
    tmp.groupby("drug_type", as_index=False)
       .agg(total_sales=("sales_amount", "sum"),
            total_claims=("total_claims", "sum"))
)

# Add percent share + nice labels
total_bg_sales = bg_df["total_sales"].sum()
bg_df["pct"] = (bg_df["total_sales"] / total_bg_sales * 100).round(2)
bg_df["sales_label"] = bg_df["total_sales"].apply(format_currency_abbrev)

# ------------------------------
# State-Level Spend Map
# ------------------------------
state_sales_df = (
    filtered_df
    .groupby("state", as_index=False)
    .agg(total_sales=("sales_amount", "sum"))
)

state_sales_df["total_sales"] = state_sales_df["total_sales"].round(2)

total_spend_all = state_sales_df["total_sales"].sum()
state_sales_df["pct_of_total"] = (state_sales_df["total_sales"] / total_spend_all * 100).round(2)

us_regions_df = state_sales_df[
    state_sales_df["state"].isin(US_STATES)
]

us_regions_df["sales_label"] = us_regions_df["total_sales"].apply(
    format_currency_abbrev
)

non_us_regions_df = state_sales_df[
    ~state_sales_df["state"].isin(US_STATES)
]

# ------------------------------
# Query KPIs
# ------------------------------

total_sales = filtered_df["sales_amount"].sum()
total_claims = filtered_df["total_claims"].sum()
avg_cost = (
    total_sales / total_claims if total_claims > 0 else 0
)
# Compute total sales by state/region
region_sales = (
    filtered_df.groupby("state", as_index=False)
    .agg(total_sales=("sales_amount", "sum"))
)

# Round for clean display
region_sales["total_sales"] = region_sales["total_sales"].round(3)

# Get top region
if not region_sales.empty:
    top_region_row = region_sales.sort_values("total_sales", ascending=False).iloc[0]
    top_region_name = top_region_row["state"]
    top_region_sales = top_region_row["total_sales"]
else:
    top_region_name = "N/A"
    top_region_sales = 0

# ------------------------------
# Streamlit Layout
# ------------------------------

# KPI Cards View
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Sales ($)", f"${total_sales:,.0f}")
col2.metric("Total Claims", f"{total_claims:,}")
col3.metric("Avg Cost per Claim ($)", f"${avg_cost:,.2f}")
col4.metric(
    "Top Region by Spend",
    f"{top_region_name}",
    f"${top_region_sales:,.0f}"
)

# Top 10 Drugs Chart View
st.subheader("Top 10 Drugs by Sales")

fig_top_10 = px.bar(
    top_drugs_df,
    x="drug_name",
    y="total_sales",
    labels={
        "drug_name": "Drug",
        "total_sales": "Total Sales ($)"
    }
)

fig_top_10.update_traces(
    text=top_drugs_df["sales_label"],
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>Total Sales: %{text}<extra></extra>"
)

fig_top_10.update_layout(
    yaxis_tickformat="~s",  # short scale
    yaxis_tickprefix="$",
    xaxis_tickangle=-45
)

st.plotly_chart(fig_top_10, width="stretch")

# Brand vs Generic Chart View
with st.container():
    st.subheader("Brand vs Generic Spend Split")

    fig_bg = px.pie(
        bg_df,
        names="drug_type",
        values="total_sales",
        hole=0.25
    )

    fig_bg.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Spend: %{customdata[0][0]}<br>"
            "Share: %{customdata[0][1]}%"
            "<extra></extra>"
            ),
        customdata = list(
            zip(
                bg_df["sales_label"], 
                bg_df["pct"]
            )
        )
    )

    st.plotly_chart(fig_bg, width="stretch", key="brand_generic_pie")

    display_df = (
        bg_df[["drug_type", "sales_label", "pct"]]
        .rename(columns={
            "drug_type": "Type",
            "sales_label": "Total Spend",
            "pct": "Percent of Total"
        })
    )
    # Format percent with % sign
    display_df["Percent of Total"] = display_df["Percent of Total"].map(lambda x: f"{x:.2f}%")
    styled_df = display_df.style.set_properties(**{
        "text-align": "left"
    })

    _, table_col, _ = st.columns([1,1.5,1])

    with table_col:

        st.dataframe(
            styled_df,
            use_container_width=True
        )


# Drug Spend Region Map/Chart View
st.subheader("Total Drug Spend by Region")

if region_view == "US States Map":
    if us_regions_df.empty:
        st.warning("No US state data available.")
    else:
        max_sales = us_regions_df["total_sales"].max()
        fig_us = px.choropleth(
            us_regions_df,
            locations="state",
            locationmode="USA-states",
            color="total_sales",
            color_continuous_scale="Blues",
            range_color=(0, max_sales),
            scope="usa",
            labels={"total_sales": "Total Sales ($)"}
        )

        fig_us.update_traces(
            hovertemplate=(
                "<b>%{location}</b><br>"
                "Total Sales: %{customdata[0]}<br>"
                "Percent of Total: %{customdata[1]}%"
                "<extra></extra>"
            ),
            customdata = list(
                zip(
                    us_regions_df["sales_label"],
                    us_regions_df["pct_of_total"]
                )
            )
        )

        fig_us.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            height=520
        )
        
        st.plotly_chart(fig_us, width="stretch")


else:
    if non_us_regions_df.empty:
        st.warning("No non-US region data available.")
    else:
        chart_df = non_us_regions_df.sort_values(
            "total_sales", ascending=False
        )
        chart_df["sales_label"] = chart_df["total_sales"].apply(
            format_currency_abbrev
        )

        fig_bar = px.bar(
            chart_df,
            x="state",
            y="total_sales",
            labels={
                "state": "Region",
                "total_sales": "Total Sales ($)"
            }
        )

        fig_bar.update_traces(
            text=chart_df["sales_label"],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Total Sales: %{text}<extra></extra>"
        )

        fig_bar.update_layout(
            yaxis_tickformat="~s",
            yaxis_tickprefix="$"
        )

        fig_bar.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            height=520
        )

        st.plotly_chart(fig_bar, width="stretch")


        st.caption("Includes U.S. territories, military regions, and CMS special jurisdictions.")

# ------------------------------
# Top 10 Drugs Detail View
# ------------------------------
st.divider()
st.subheader("Top 10 Drugs by Selected Region")

available_regions = sorted(state_sales_df["state"].unique())

default_index = (
    available_regions.index("PA")
    if "PA" in available_regions
    else 0
)

selected_region = st.selectbox(
    "Choose a state/region to view its Top 10 drugs",
    options=available_regions,
    index=default_index
)

region_top10 = (
    top10_by_state[top10_by_state["state"] == selected_region]
    .sort_values("rank")
    .copy()
)

region_top10["Total Sales"] = region_top10["total_sales"].apply(format_currency_abbrev)
region_top10["% of State Total"] = region_top10["pct_of_state"].round(2).astype(str) + "%"

cols = st.columns(2)

for i, (_, row) in enumerate(region_top10.iterrows()):
    with cols[i % 2]:
        st.metric(
            label=row["drug_name"],
            value=format_currency_abbrev(row["total_sales"]),
            delta=f"{row['pct_of_state']:.2f}% of region"
        )



