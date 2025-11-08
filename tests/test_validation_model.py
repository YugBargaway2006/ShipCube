# tests/test_validation_models.py
import pytest
from pydantic import ValidationError
from datetime import datetime, timezone
from ml.validation_model import Tracking as TrackingModel



def test_tracking_model_success():
    """Tests that valid data is parsed correctly."""
    data = {
        "order_id": "13465123",
        "status": "In Transit",
        "order_insert_timestamp": "2025-11-05T10:00:00Z",
        "label_generation_timestamp": "2025-11-10T17:00:00Z",
    }
    model = TrackingModel(**data)
    assert model.order_id == "13465123"
    assert model.order_insert_timestamp == datetime(2025, 11, 5, 10, 0, tzinfo=timezone.utc)

def test_tracking_model_invalid_date():
    """Tests that a bad date raises a ValidationError."""
    data = {
        "order_id": "13465123",
        "status": "In Transit",
        "order_insert_timestamp": "not a date",
        "label_generation_timestamp": "2025-11-10T17:00:00Z"
    }
    with pytest.raises(ValidationError):
        TrackingModel(**data)

def test_tracking_model_missing_field():
    """Tests that a missing required field raises a ValidationError."""
    data = {
        # "order_id": "13465123",
        "status": "In Transit",
        "order_insert_timestamp": "not a date",
        "label_generation_timestamp": "2025-11-10T17:00:00Z"
    }
    with pytest.raises(ValidationError):
        TrackingModel(**data)

