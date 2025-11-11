# tests/conftest.py
import pytest
import pandas as pd
from unittest.mock import MagicMock
from ml.validation_model import Tracking  # Import your real model


@pytest.fixture
def mock_engine_and_conn():
    """Mocks engine.begin() context manager with DB connection."""
    mock_engine = MagicMock()
    mock_conn = MagicMock()
    
    # Properly mock engine.begin() context manager
    mock_engine.begin.return_value.__enter__.return_value = mock_conn
    mock_engine.begin.return_value.__exit__.return_value = None

    return mock_engine, mock_conn


@pytest.fixture
def mock_raw_conn_cursor(mock_engine_and_conn):
    """Mocks the raw_connection and cursor for bulk loading."""
    mock_engine, _ = mock_engine_and_conn
    mock_cursor = MagicMock()
    mock_raw_conn = MagicMock()
    mock_raw_conn.cursor.return_value = mock_cursor
    mock_engine.raw_connection.return_value = mock_raw_conn
    return mock_raw_conn, mock_cursor

@pytest.fixture
def sample_mapping_config_yaml():
    """Provides the sample YAML config as a file string."""
    
    return """
                tracking_ingest:
                model_key: "tracking"
                target_table: "tracking"
                primary_key: "order_id"
                columns:
                    - { source: "Order_ID", target: "order_id" }
                    - { source: "Order Insert Timestamp", target: "order_insert_timestamp" }
           """

@pytest.fixture
def mock_valid_dataframe():
    """A mock DataFrame with one valid row."""
    df = pd.DataFrame({
        'Order_ID': ['ORD123'],
        'Order Insert Timestamp': ['2024-01-15 10:30:00']
    })
    # Create a mock that will be returned by pd.read_csv
    mock_df = MagicMock(spec=pd.DataFrame)
    mock_df.to_dict.return_value = df.to_dict('records')
    mock_df.to_csv = MagicMock()
    mock_df.__len__.return_value = len(df)
    return mock_df

@pytest.fixture
def mock_invalid_dataframe():
    """A mock DataFrame with one invalid row (bad date)."""
    df = pd.DataFrame({
        'Order_ID': ['ORD456'],
        'Order Insert Timestamp': ['not-a-date']
    })
    # Create a mock that will be returned by pd.read_csv
    mock_df = MagicMock(spec=pd.DataFrame)
    mock_df.to_dict.return_value = df.to_dict('records')
    mock_df.__len__.return_value = len(df)
    return mock_df

@pytest.fixture
def mock_get_validator(mocker):
    """Mocks the get_validator_model helper."""
    # Return the real Tracking model
    return mocker.patch('etl.utils.get_validator_model', return_value=Tracking)