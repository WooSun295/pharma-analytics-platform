import pandas as pd

USE_COLS = [
    "Prscrbr_NPI",
    "Prscrbr_State_Abrvtn",
    "Prscrbr_Type",
    "Brnd_Name",
    "Gnrc_Name",
    "Tot_Clms",
    "Tot_Drug_Cst"
]

def extract_data(csv_path, chunk_size=100_000):
    """
    Generates raw filtered CMS data chunks.
    """
    return pd.read_csv(
        csv_path,
        usecols=USE_COLS,
        chunksize=chunk_size
    )
