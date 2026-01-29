import pandas as pd
import os

DEFAULT_CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 50_000))

USE_COLS = [
    "Prscrbr_NPI",
    "Prscrbr_State_Abrvtn",
    "Prscrbr_Type",
    "Brnd_Name",
    "Gnrc_Name",
    "Tot_Clms",
    "Tot_Drug_Cst"
]

def extract_data(csv_path, chunk_size=DEFAULT_CHUNK_SIZE):
    """
    Generates raw filtered CMS data chunks.
    """
    return pd.read_csv(
        csv_path,
        usecols=USE_COLS,
        chunksize=chunk_size,
        low_memory=False
    )
