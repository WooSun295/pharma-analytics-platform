import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from extract import extract_data
from transform import transform_chunk
from load import load_dimensions, load_facts
from pathlib import Path
import time

load_dotenv()

CSV_PATH = os.getenv("CSV_PATH")
DB_URI = os.getenv("DB_URI")

def run_schema(engine, schema_path=None):
    if schema_path is None:
        schema_path = Path(__file__).resolve().parent.parent / "sql" / "schema.sql"
    
    ddl = Path(schema_path).read_text(encoding="utf-8")

    with engine.begin() as conn:
        conn.execute(text(ddl))

# CSV_PATH = r"data\SAMEPLE_RAW_CMS_DATA_1000.csv"

if not CSV_PATH or not DB_URI:
    raise ValueError("Missing environment variables: CSV_PATH or DB_URI")

engine = create_engine(DB_URI)

print("Creating schema...", flush=True)
run_schema(engine)
print("Schema ready. Beginning chunk loop...", flush=True)

i = 0

for raw_chunk in extract_data(CSV_PATH):
    i += 1

    transformed = transform_chunk(raw_chunk)

    if transformed.empty:
        continue

    t0 = time.time()
    load_dimensions(transformed, engine)
    print(f"Chunk {i}: Load Dimensions took {time.time()-t0:.1f}s")

    t1 = time.time()
    load_facts(transformed, engine)
    print(f"Chunk {i}: Load Facts took {time.time()-t0:.1f}s")

    print(f"Chunk {i}: loaded ~{len(raw_chunk):,} raw rows, {len(transformed):,} transformed rows", flush=True)

print("ETL pipeline completed successfully.")
