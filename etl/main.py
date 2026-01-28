import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from extract import extract_data
from transform import transform_chunk
from load import load_dimensions, load_facts

load_dotenv()

CSV_PATH = os.getenv("CSV_PATH")
DB_URI = os.getenv("DB_URI")

def run_schema(engine, schema_path="../sql/schema.sql"):
    with open(schema_path, "r") as f:
        ddl = f.read()

    with engine.begin() as conn:
        conn.execute(text(ddl))

# CSV_PATH = r"data\SAMEPLE_RAW_CMS_DATA_1000.csv"

if not CSV_PATH or not DB_URI:
    raise ValueError("Missing environment variables: CSV_PATH or DB_URI")

engine = create_engine(DB_URI)

run_schema(engine)

i = 1

for raw_chunk in extract_data(CSV_PATH):
    transformed = transform_chunk(raw_chunk)

    if transformed.empty:
        continue

    load_dimensions(transformed, engine)
    load_facts(transformed, engine)

    if i < 267:
        print(f"Loaded {i*100_000} rows")

print("ETL pipeline completed successfully.")
