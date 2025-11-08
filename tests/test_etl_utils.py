# tests/test_etl_utils.py

import pytest
from sqlalchemy import Table
from ml.validation_model import Tracking
from etl.utils import get_validator_model, get_sqlalchemy_table


def test_get_validator_model_success():
    """Tests that the correct Pydantic model is returned."""
    model = get_validator_model("tracking")
    assert model == Tracking


def test_get_validator_model_fail():
    """Tests that a bad name raises a ValueError."""
    with pytest.raises(ValueError, match="No validator model found"):
        get_validator_model("non_existent_table")


def test_get_sqlalchemy_table(mocker, mock_engine):
    """Tests that the Table reflection is called correctly."""
    
    mock_table_class = mocker.patch("etl.utils.Table", autospec=True)
    
    result = get_sqlalchemy_table("tracking", mock_engine)
    
    mock_table_class.assert_called_once_with(
        "tracking",
        mocker.ANY,
        autoload_with=mock_engine
    )

    assert result == mock_table_class.return_value