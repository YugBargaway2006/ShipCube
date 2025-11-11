# tests/test_etl_load_data.py
import pandas as pd
import pytest
import yaml
from unittest.mock import patch, mock_open, call, MagicMock

# Import the functions we are testing
from etl.load_data import load_incremental_data as load_data
from etl.bulk_load_initial import bulk_load_historical


def test_load_data_success(mocker, mock_engine_and_conn, 
                           sample_mapping_config_yaml, mock_valid_dataframe,
                           mock_get_validator):
    """
    Tests the full 'happy path' of the incremental load.
    It checks that valid data is read, validated, and upserted.
    """

    mock_engine, mock_db_conn = mock_engine_and_conn

    config_dict = yaml.safe_load(sample_mapping_config_yaml)
    mocker.patch('etl.load_data.yaml.safe_load', return_value=config_dict)
    mocker.patch('pandas.read_csv', return_value=mock_valid_dataframe)
    mocker.patch('csv.DictWriter', autospec=True)
    
    mock_table = MagicMock()
    mocker.patch('etl.utils.get_sqlalchemy_table', return_value=mock_table)
    
    failed_records = load_data(
        csv_path='dummy.csv', 
        config_key='tracking_ingest', 
        engine=mock_engine
    )
    
    mock_engine.begin.assert_called_once()
    mock_db_conn.execute.assert_called_once()

    executed_sql_obj = mock_db_conn.execute.call_args[0][0]
    sql_string = str(executed_sql_obj)
    
    assert len(failed_records) == 0
    assert "INSERT INTO" in sql_string.upper()
    assert "ON CONFLICT" in sql_string.upper()


def test_load_data_validation_error_dlq(mocker, mock_engine_and_conn,
                                        sample_mapping_config_yaml, mock_invalid_dataframe,
                                        mock_get_validator):
    """
    Tests the 'error path' where Pydantic validation fails.
    Checks that the DLQ file is written to and the database is NOT called.
    """

    mock_engine, mock_db_conn = mock_engine_and_conn
    # 1. Mock the config file loading
    config_dict = yaml.safe_load(sample_mapping_config_yaml)
    mocker.patch('etl.load_data.config', config_dict)
    
    # 2. Mock file reads, this time returning an *invalid* DataFrame
    mocker.patch('pandas.read_csv', return_value=mock_invalid_dataframe)
    
    # 3. Mock the csv.DictWriter to check what's written to the DLQ
    mock_writer = MagicMock()
    mocker.patch('csv.DictWriter', return_value=mock_writer)
    
    # 4. Mock the file open operation
    m_open = mock_open()
    mocker.patch('builtins.open', m_open)
    
    # --- Act ---
    failed_records = load_data(
        csv_path='dummy.csv', 
        config_key='tracking_ingest', 
        engine=mock_engine
    )
    
    # --- Assert ---
    # 1. Check that one record failed
    assert len(failed_records) == 1
    assert "validation_error" in failed_records[0]
    
    # 2. Check that the DLQ was written to
    mock_writer.writeheader.assert_called()
    mock_writer.writerow.assert_called()
    
    # 3. Check that the database was NEVER called (because no rows were valid)
    mock_engine.begin.assert_not_called()
    mock_db_conn.execute.assert_not_called()


def test_bulk_load_historical(mocker, mock_engine_and_conn, mock_raw_conn_cursor, mock_valid_dataframe):
    """
    Tests the high-speed bulk load script.
    Checks that 'copy_from' is used.
    """

    mock_engine, _ = mock_engine_and_conn
    # 1. Mock file reads
    mocker.patch('pandas.read_csv', return_value=mock_valid_dataframe)
    
    # 2. Mock the in-memory buffer 'io.StringIO'
    mock_buffer = MagicMock()
    mocker.patch('io.StringIO', return_value=mock_buffer)
    
    # 3. Get the mock connection and cursor
    mock_conn, mock_cursor = mock_raw_conn_cursor
    
    # --- Act ---
    bulk_load_historical(
        csv_path='dummy_bulk.csv', 
        table_name='tracking', 
        engine=mock_engine
    )
    
    # --- Assert ---
    # 1. Check that df.to_csv was called (no header, no index)
    mock_valid_dataframe.to_csv.assert_called_with(mock_buffer, index=False, header=False)
    
    # 2. Check that the high-speed 'copy_from' was called
    mock_cursor.copy_from.assert_called_once_with(mock_buffer, 'tracking', sep=',', null="")
    
    # 3. Check that the transaction was committed
    mock_conn.commit.assert_called_once()