from sqlalchemy import Table, MetaData
from sqlalchemy.exc import NoSuchTableError

from ml.validation_model import Tracking, Customer, RateTable


_METADATA = MetaData()   # Global MetaData Object
_TABLE_CACHE = {}

VALIDATOR_REGISTRY = {
    "tracking": Tracking,
    "customers": Customer,
    "rate_table": RateTable,
    # "customer_contracts": CustomerContractModel,
}


def get_sqlalchemy_table(table_name: str, engine):
    """
    Fetches a SQLAlchemy Table object by reflecting the database.
    Caches the result for performance.
    """
    
    if table_name in _TABLE_CACHE:
        return _TABLE_CACHE[table_name]
        
    try:
        table = Table(
            table_name,
            _METADATA,
            autoload_with=engine
        )
        
        _TABLE_CACHE[table_name] = table
        return table
        
    except NoSuchTableError:
        raise ValueError(f"Table '{table_name}' does not exist in the database. "
                         "Please run the DDL from Table 1.")
    except Exception as e:
        raise RuntimeError(f"Could not reflect table '{table_name}'. Error: {e}")
    


def get_validator_model(model_name: str):
    """
    Fetches the correct Pydantic validation model from the registry
    based on the table name.
    """
    model = VALIDATOR_REGISTRY.get(model_name)

    if not model:
        raise ValueError(f"No validator model found for '{model_name}'. "
                         f"Check VALIDATOR_REGISTRY in etl/utils.py.")
                         
    return model

