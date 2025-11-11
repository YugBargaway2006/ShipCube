import pandas as pd
import logging
import csv 
import yaml
import sys
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from pydantic import ValidationError

from etl.utils import get_validator_model, get_sqlalchemy_table


DB_CONN_STRING = "postgresql://your_user:your_password@localhost:5432/your_db_name"


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers= [logging.StreamHandler(sys.stdout)]
)


DLQ_FILE_PATH_TEMPLATE = '{config_key}_failures.csv'


try:
    with open("config/schema_mapping.yml", 'r') as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    logging.error("FATAL: config/schema_mapping.yml not found. Make sure you are running this script from the project's root directory.")
    sys.exit(1)



def load_incremental_data(csv_path: str, config_key: str, engine):
    """
    Validates and upserts data from a CSV to a target table.
    This process is idempotent and implements DLQ logic.
    """
    
    try:
        mapping = config[config_key]
        ValidatorModel = get_validator_model(mapping['model_key'])

        target_table_name = mapping['target_table']
        pk_column = mapping['primary_key']
    except KeyError:
        logging.error(f"No config or model found for key: {config_key}. Skipping.")
        return []
    except Exception as e:
        logging.error(f"Failed to load config for {config_key}: {e}")
        return []

    
    column_map = {col['source']: col['target'] for col in mapping['columns']}
    try:
        df = pd.read_csv(csv_path, usecols=column_map.keys()).rename(columns=column_map)
    except FileNotFoundError:
        logging.error(f"[{config_key}] File not found: {csv_path}")
        return []
    except Exception as e:
        logging.error(f"[{config_key}] Error reading CSV: {e}")
        return []

    valid_records = []
    failed_records = []
    dlq_header_written = False
    dlq_file_path = DLQ_FILE_PATH_TEMPLATE.format(config_key=config_key)

    logging.info(f"[{config_key}] Starting validation for {len(df)} rows from {csv_path}...")

    for record in df.to_dict('records'):
        try:
            valid_model = ValidatorModel(**record)
            valid_records.append(valid_model.dict())
        except ValidationError as e:
            logging.warning(f"Validation failed for row: {record}. Error: {e}")
            failed_row_data = {"original_data": record, "validation_error": str(e)}
            failed_records.append(failed_row_data)
            
            try:
                with open(dlq_file_path, 'a', newline='', encoding='utf-8') as f:
                    fieldnames = failed_row_data.keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    
                    if not dlq_header_written and f.tell() == 0:
                        writer.writeheader()
                        dlq_header_written = True
                        
                    writer.writerow(failed_row_data)
            except IOError as dlq_e:
                logging.error(f"FATAL: Could not write to DLQ file at {dlq_file_path}. Error: {dlq_e}")
            # ---------------------------------------------------

    logging.info(f"Validation complete. Valid: {len(valid_records)}. Failed: {len(failed_records)} (details in {dlq_file_path}).")
    
    if not valid_records:
        logging.info(f"[{config_key}] No valid records to load.")
        return []

    try:
        table = get_sqlalchemy_table(target_table_name, engine)
        
        insert_stmt = insert(table).values(valid_records)
        
        update_columns = {
            c.name: c
            for c in insert_stmt.excluded
            if c.name!= pk_column
        }
        
        upsert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[pk_column],
            set_=update_columns
        )
        
        with engine.begin() as conn:
            conn.execute(upsert_stmt)
            
        logging.info(f"[{config_key}] Successfully upserted {len(valid_records)} records to {target_table_name}.")
        
    except Exception as load_e:
        logging.error(f"[{config_key}] Database load failed: {load_e}")
        logging.error("No data from this batch was loaded. Check database/permissions.")
        return failed_records

    return failed_records



if __name__ == "__main__":
    if DB_CONN_STRING == "postgresql://your_user:your_password@localhost:5432/your_db_name":
        logging.error("Please update DB_CONN_STRING in etl/load_data.py")
    else:
        try:
            engine = create_engine(DB_CONN_STRING)
            
            pipeline_jobs = {
                "tracking_ingest": "data/tracking_updates.csv",
                "rate_ingest": "data/new_rates.csv",
                "customer_ingest": "data/new_customers.csv",
                "contract_ingest": "data/new_contracts.csv"
            }
            
            for config_key, csv_path in pipeline_jobs.items():
                if config_key in config:
                    logging.info(f"--- Starting job: {config_key} ---")
                    load_incremental_data(
                        csv_path=csv_path, 
                        config_key=config_key, 
                        engine=engine
                    )
                else:
                    logging.warning(f"Skipping job: '{config_key}' not found in schema_mapping.yml")

        except Exception as e:
            logging.error(f"Pipeline failed: {e}")