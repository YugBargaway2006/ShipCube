# etl/bulk_load_initial.py

import pandas as pd
import psycopg2
import io
import logging
from sqlalchemy import create_engine


DB_CONN_STRING = "postgresql://postgres:postgres@localhost:5432/customerdb"

SOURCE_CSV_FILE = "backend/src/ingest_pipeline/5_Dog Is Human Nov - 24.csv"
TARGET_TABLE_NAME = "tracking"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



def bulk_load_historical(csv_path: str, table_name: str, engine):
    """
    Performs a high-speed initial bulk load using COPY.
    This is NOT idempotent and should only be run on an empty table.
    """

    logging.info(f"Starting high-speed bulk load for {table_name} from {csv_path}...")

    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        logging.error(f"File not found: {csv_path}")
        return
    except Exception as e:
        logging.error(f"Error reading CSV: {e}")
        return 
    
    
    conn = None
    try:
        conn = engine.raw_connection()
        cursor = conn.cursor()
        
        buffer = io.StringIO()
        df.to_csv(buffer, index=False, header=False)
        buffer.seek(0)
        
        logging.info(f"Executing COPY to {table_name}...")
        cursor.copy_from(buffer, table_name, sep=',', null="")
        conn.commit()
        
        logging.info(f"Successfully bulk-loaded {len(df)} records to {table_name}.")
        
    except (Exception) as e:
        if conn:
            conn.rollback()
        logging.error(f"Error during bulk load: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    if DB_CONN_STRING == "postgresql://your_user:your_password@localhost:5432/your_db_name":
        logging.error("Please update DB_CONN_STRING in etl/bulk_load_initial.py")
    else:
        try:
            engine = create_engine(DB_CONN_STRING)
            bulk_load_historical(SOURCE_CSV_FILE, TARGET_TABLE_NAME, engine)
        except Exception as e:
            logging.error(f"Pipeline failed: {e}")