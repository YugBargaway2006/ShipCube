# models/validation_models.py

import pydantic
import json
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, field_validator, TypeAdapter, ValidationError


# --- Sub-models (for JSONB fields) ---

class LocationEvent(pydantic.BaseModel):
    """
    A Pydantic sub-model to validate one entry in the
    'location_history' JSONB array of the 'tracking' table.
    """
    timestamp: datetime
    location: str
    status: str

# --- Main Table Validation Models ---

class TrackingModel(pydantic.BaseModel):
    """
    Validates data intended for the 'tracking' table.
    """
    order_id: str
    customer_id: Optional[str] = None
    status: str
    location_history: Optional[List[LocationEvent]] = None
    last_event_time: datetime
    estimated_delivery: Optional[datetime] = None
    last_updated: Optional[datetime] = None

    @pydantic.field_validator('location_history', pre=True)
    def parse_location_history_from_string(cls, v):
        """
        Validator to ensure that if 'location_history' is provided
        as a JSON string from the CSV, it is parsed into the
        correct list of LocationEvent objects.[4]
        """
        if isinstance(v, str):
            try:
                # Parse the JSON string
                data = json.loads(v)
                # Validate the parsed data against the sub-model
                return pydantic.TypeAdapter.validate_python(List[LocationEvent], data)
            except (json.JSONDecodeError, TypeError, ValidationError):
                # If parsing fails, return None or raise an error
                return None
        return v

class CustomerModel(pydantic.BaseModel):
    """
    Validates data intended for the 'customers' table.
    """
    customer_id: UUID
    customer_name: str
    contact_email: Optional[str] = None
    account_tier: Optional[str] = 'standard'
    created_at: Optional[datetime] = None

    @pydantic.validator('account_tier')
    def validate_account_tier(cls, v):
        """
        Ensures 'account_tier' is one of the allowed ENUM values.
        """
        allowed_tiers = {'standard', 'premium', 'enterprise'}
        if v not in allowed_tiers:
            raise ValueError(f"Invalid account_tier: '{v}'. Must be one of {allowed_tiers}")
        return v

class CustomerContractModel(pydantic.BaseModel):
    """
    Validates data intended for the 'customer_contracts' table.
    """
    contract_id: Optional[str] = None
    customer_id: UUID
    contract_details: Optional[str] = None
    effective_date: date
    expiration_date: Optional[date] = None
    last_updated: Optional[datetime] = None

    @pydantic.validator('contract_details', pre=True)
    def parse_contract_details_from_string(cls, v):
        """
        Validator to ensure that if 'contract_details' is provided
        as a JSON string from the CSV, it is parsed into a Python dict.
        """
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return None
        return v

class RateTableModel(pydantic.BaseModel):
    """
    Validates data intended for the 'rate_table' table.
    Uses Decimal for precise currency representation.
    """
    route_id: Optional[str] = None
    origin: str
    destination: str
    product_id: str
    effective_date: date
    base_rate: Decimal
    surcharge_type: Optional[str] = None
    surcharge_value: Optional[str] = None
    currency: str
    last_updated: Optional[datetime] = None

    class Config:
        # Allows Pydantic to handle the 'Decimal' type
        arbitrary_types_allowed = True