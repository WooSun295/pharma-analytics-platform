from sqlalchemy import text

def load_dimensions(df, engine):
    """
    Loads dimension tables (drug, provider).
    """
    drugs = df[["drug_name", "generic_name"]].drop_duplicates()
    providers = df[["prescriber_npi", "state", "provider_type"]].drop_duplicates()

    with engine.begin() as conn:
        # Upsert drugs
        for _, row in drugs.iterrows():
            conn.execute(
                text("""
                    INSERT INTO dim_drug (drug_name, generic_name)
                    VALUES (:drug_name, :generic_name)
                    ON CONFLICT (drug_name) DO NOTHING
                """),
                {"drug_name": row["drug_name"], "generic_name": row["generic_name"]}
            )

        for _, row in providers.iterrows():
            conn.execute(
                text("""
                    INSERT INTO dim_provider (prescriber_npi, state, provider_type)
                    VALUES (:prescriber_npi, :state, :provider_type)
                    ON CONFLICT (prescriber_npi) DO NOTHING
                """),
                {"prescriber_npi": row["prescriber_npi"],
                 "state": row["state"],
                 "provider_type": row["provider_type"]}
            )


def load_facts(df, engine):
    """
    Loads fact_sales table using dimension lookups.
    """
    with engine.begin() as conn:
        # Stage facts
        df[[
            "prescriber_npi",
            "drug_name",
            "total_claims",
            "sales_amount"
        ]].to_sql(
            "temp_fact",
            conn,
            if_exists="replace",
            index=False
        )

        insert_sql = text("""
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
              ON tf.prescriber_npi = p.prescriber_npi
        """)

        conn.execute(insert_sql, {"sale_year": int(df["sale_year"].iloc[0])})
