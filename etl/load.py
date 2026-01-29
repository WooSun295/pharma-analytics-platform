from sqlalchemy import text
from io import StringIO

def load_dimensions(df, engine):
    """
    Fast RDS-friendly dimension load:
    COPY into temp tables, then INSERT DISTINCT ... ON CONFLICT DO NOTHING
    """
    drugs = df[["drug_name", "generic_name"]].drop_duplicates().copy()
    providers = df[["prescriber_npi", "state", "provider_type"]].drop_duplicates().copy()

    # Ensure simple Python/string types for CSV/COPY
    drugs["drug_name"] = drugs["drug_name"].astype(str)
    drugs["generic_name"] = drugs["generic_name"].astype("string")

    providers["prescriber_npi"] = providers["prescriber_npi"].astype(str)
    providers["state"] = providers["state"].astype(str)
    providers["provider_type"] = providers["provider_type"].astype(str)

    with engine.begin() as conn:
        conn.execute(text("SET LOCAL synchronous_commit = OFF;"))
        conn.execute(text("SET LOCAL work_mem = '64MB';"))

        # TEMP staging tables live only for this transaction
        conn.execute(text("""
            CREATE TEMP TABLE temp_drug_dim (
                drug_name TEXT,
                generic_name TEXT
            ) ON COMMIT DROP;

            CREATE TEMP TABLE temp_provider_dim (
                prescriber_npi TEXT,
                state TEXT,
                provider_type TEXT
            ) ON COMMIT DROP;
        """))

        # COPY drugs
        drug_buf = StringIO()
        drugs.to_csv(drug_buf, index=False, header=False)
        drug_buf.seek(0)

        # COPY providers
        prov_buf = StringIO()
        providers.to_csv(prov_buf, index=False, header=False)
        prov_buf.seek(0)

        dbapi_conn = conn.connection.driver_connection  # SQLAlchemy 2.x + psycopg2
        cur = dbapi_conn.cursor()
        try:
            cur.copy_expert(
                "COPY temp_drug_dim (drug_name, generic_name) FROM STDIN WITH (FORMAT CSV)",
                drug_buf
            )
            cur.copy_expert(
                "COPY temp_provider_dim (prescriber_npi, state, provider_type) FROM STDIN WITH (FORMAT CSV)",
                prov_buf
            )
        finally:
            cur.close()

        # Set-based upsert into dims (1 statement each)
        conn.execute(text("""
            INSERT INTO dim_drug (drug_name, generic_name)
            SELECT DISTINCT drug_name, generic_name
            FROM temp_drug_dim
            WHERE drug_name IS NOT NULL
            ON CONFLICT (drug_name) DO NOTHING;
        """))

        conn.execute(text("""
            INSERT INTO dim_provider (prescriber_npi, state, provider_type)
            SELECT DISTINCT prescriber_npi, state, provider_type
            FROM temp_provider_dim
            WHERE prescriber_npi IS NOT NULL
            ON CONFLICT (prescriber_npi) DO NOTHING;
        """))




def load_facts(df, engine):
    """
    Faster fact load:
    COPY into TEMP, ANALYZE, then set-based INSERT JOIN.
    No temp indexes per chunk.
    """
    sale_year = int(df["sale_year"].iloc[0])

    stage = df[["prescriber_npi", "drug_name", "total_claims", "sales_amount"]].copy()
    stage["prescriber_npi"] = stage["prescriber_npi"].astype(str)
    stage["drug_name"] = stage["drug_name"].astype(str)
    stage["total_claims"] = stage["total_claims"].astype("Int64")
    stage["sales_amount"] = stage["sales_amount"].astype(float)

    with engine.begin() as conn:
        conn.execute(text("SET LOCAL synchronous_commit = OFF;"))
        conn.execute(text("SET LOCAL work_mem = '64MB';"))
        
        # Temp table per transaction
        conn.execute(text("""
            CREATE TEMP TABLE temp_fact (
                prescriber_npi TEXT,
                drug_name TEXT,
                total_claims BIGINT,
                sales_amount DOUBLE PRECISION
            ) ON COMMIT DROP;
        """))

        csv_buf = StringIO()
        stage.to_csv(csv_buf, index=False, header=False)
        csv_buf.seek(0)

        dbapi_conn = conn.connection.driver_connection
        cur = dbapi_conn.cursor()
        try:
            cur.copy_expert(
                "COPY temp_fact (prescriber_npi, drug_name, total_claims, sales_amount) FROM STDIN WITH (FORMAT CSV)",
                csv_buf
            )
        finally:
            cur.close()

        # Help the planner choose good joins on temp table
        conn.execute(text("ANALYZE temp_fact;"))

        conn.execute(text("""
            INSERT INTO fact_sales (
                drug_id,
                provider_id,
                sale_year,
                total_claims,
                sales_amount
            )
            SELECT
                d.drug_id,
                p.provider_id,
                :sale_year,
                tf.total_claims,
                tf.sales_amount
            FROM temp_fact tf
            JOIN dim_drug d
              ON tf.drug_name = d.drug_name
            JOIN dim_provider p
              ON tf.prescriber_npi = p.prescriber_npi;
        """), {"sale_year": sale_year})
