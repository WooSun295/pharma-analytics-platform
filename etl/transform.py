import pandas as pd

SALE_YEAR = 2023

def transform_chunk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and transforms extracted data chunks.
    """
    # Replace suppression flags
    df = df.replace("*", pd.NA)

    # Drop rows missing critical fields
    df = df.dropna(subset=[
        "Prscrbr_NPI",
        "Brnd_Name",
        "Tot_Drug_Cst"
    ])

    # Rename columns to warehouse-friendly names
    df = df.rename(columns={
        "Prscrbr_NPI": "prescriber_npi",
        "Prscrbr_State_Abrvtn": "state",
        "Prscrbr_Type": "provider_type",
        "Brnd_Name": "drug_name",
        "Gnrc_Name": "generic_name",
        "Tot_Clms": "total_claims",
        "Tot_Drug_Cst": "sales_amount"
    })

    # Add derived fields
    df["sale_year"] = SALE_YEAR

    # Force Python native types
    df["total_claims"] = df["total_claims"].astype("Int64")
    df["sales_amount"] = df["sales_amount"].astype(float)
    df["prescriber_npi"] = df["prescriber_npi"].astype(str)
    df["sale_year"] = df["sale_year"].apply(lambda x: int(x) if pd.notna(x) else None)

    return df
