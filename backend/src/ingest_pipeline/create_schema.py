from sqlalchemy import create_engine, text

DB_CONN_STRING = "postgresql://postgres:postgres@localhost:5432/customerdb"
SCHEMA_PATH = "backend/src/ingest_pipeline/schema.sql"


# To be run only once to create the schema in PostgreSQL

engine = create_engine(DB_CONN_STRING)

with open(SCHEMA_PATH, "r") as f:
    schema_sql = f.read()

with engine.begin() as conn:
    conn.execute(text(schema_sql))

print("Schema successfully created in PostgreSQL.")
