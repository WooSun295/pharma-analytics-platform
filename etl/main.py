import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from extract import extract_data
from transform import transform_chunk
from load import load_dimensions, load_facts

load_dotenv()

CSV_PATH = os.getenv("CSV_PATH")
DB_URI = os.getenv("DB_URI")

# CSV_PATH = r"data\SAMEPLE_RAW_CMS_DATA_1000.csv"

if not CSV_PATH or not DB_URI:
    raise ValueError("Missing environment variables: CSV_PATH or DB_URI")

engine = create_engine(DB_URI)

for raw_chunk in extract_data(CSV_PATH):
    transformed = transform_chunk(raw_chunk)

    if transformed.empty:
        continue

    load_dimensions(transformed, engine)
    load_facts(transformed, engine)

print("ETL pipeline completed successfully.")
