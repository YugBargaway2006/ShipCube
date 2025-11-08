# models/validation_models.py

import pydantic
import json
import datetime as dt
from decimal import Decimal
from uuid import UUID, uuid4
from typing import Optional, Annotated
from pydantic import BaseModel
from pydantic import BaseModel, Field, EmailStr, field_validator


# --- Sub-models (for JSONB fields) ---

# class LocationEvent(pydantic.BaseModel):
#     """
#     A Pydantic sub-model to validate one entry in the
#     'location_history' JSONB array of the 'tracking' table.
#     """
#     timestamp: datetime
#     location: str
#     status: str


# --- Main Table Validation Models ---

class Customer(BaseModel):
    customer_id: UUID = Field(
        default_factory=uuid4,
        description="Unique customer ID"
    )

    customer_name: Annotated[str, Field(min_length=1)] = Field(
        ..., description="Full name of the customer"
    )

    contact_email: Optional[EmailStr] = Field(
        None, 
        description="Unique email of the customer"
    )

    account_tier: Annotated[str, Field(max_length=20)] = Field(
        default="visitor", description="Tier of the account (visitor/client)"
    )

    created_at: dt.datetime = Field(
        default_factory=lambda: dt.datetime.now(dt.timezone.utc), 
        description="Record creation timestamp"
    )
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "customer_name": "John Doe",
                "contact_email": "john@example.com",
                "account_tier": "client"
            }
        }
    }

    @field_validator("customer_name", "account_tier", mode="before")
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class Tracking(BaseModel):
    order_id: str = Field(..., description="Primary key for the order")
    user_id: Optional[int] = None
    merchant_name: Optional[str] = None
    customer_name: Optional[str] = None
    transaction_status: Optional[str] = None
    transaction_type: Optional[str] = None
    invoice_number: Optional[int] = None
    transaction_date: Optional[dt.datetime] = None
    store_order_id: Optional[int] = None
    tracking_id: Optional[str] = None
    fulfillment_without_surcharge: Optional[Decimal] = None
    surcharge_applied: Optional[Decimal] = None
    invoice_amount: Optional[Decimal] = None
    wms_fuel_surcharge: Optional[Decimal] = None
    delivery_area_surcharge: Optional[Decimal] = None
    address_correction: Optional[int] = None
    insurance_amount: Optional[Decimal] = None
    final_invoice_amt: Optional[Decimal] = None
    products_sold: Optional[str] = None
    total_quantity: Optional[int] = None
    ship_option_id: Optional[int] = None
    carrier: Optional[str] = None
    carrier_service: Optional[str] = None
    zone_used: Optional[str] = None
    actual_weight_oz: Optional[Decimal] = None
    dim_weight_oz: Optional[Decimal] = None
    billable_weight_oz: Optional[Decimal] = None
    length: Optional[Decimal] = None
    width: Optional[Decimal] = None
    height: Optional[Decimal] = None
    zip_code: Optional[str] = None
    city: Optional[str] = None
    destination_country: Optional[str] = None
    order_insert_timestamp: Optional[dt.datetime] = None
    label_generation_timestamp: Optional[dt.datetime] = None
    fc_name: Optional[str] = None
    order_category: Optional[str] = None
    final_invoice_amt_added_50c: Optional[Decimal] = None
    last_updated: dt.datetime = Field(default_factory=lambda: dt.datetime.now(dt.timezone.utc))
    customer_id: Optional[UUID] = Field(None, description="Foreign key reference to customers")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "order_id": "ORD123",
                "transaction_status": "Delivered",
                "invoice_amount": "125.50",
                "carrier": "FedEx",
                "customer_id": "3a28a59d-8b4b-44a1-9b16-32c90dc5a0f3"
            }
        }
    }


class RateTable(BaseModel):
    route_id: UUID = Field(
        default_factory=uuid4, 
        description="Unique route ID"
    )

    origin: Annotated[str, Field(max_length=100)] = Field(
        ..., description="Origin location"
    )

    destination: Annotated[str, Field(max_length=100)] = Field(
        ..., description="Destination location"
    )

    product_id: Annotated[str, Field(max_length=50)] = Field(
        ..., description="Product ID or code"
    )

    effective_date: dt.date = Field(
        ..., description="Effective date of rate"
    )

    base_rate: Decimal = Field(
        ..., description="Base rate"
    )

    surcharge_type: Optional[Annotated[str, Field(max_length=50)]] = Field(None)
    surcharge_value: Optional[Decimal] = Field(None)
    
    currency: Annotated[str, Field(min_length=3, max_length=3)] = Field(
        ..., description="ISO 4217 currency code"
    )

    last_updated: dt.datetime = Field(
        default_factory=lambda: dt.datetime.now(dt.timezone.utc), description="Timestamp of last update"
    )

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "origin": "New York",
                "destination": "Los Angeles",
                "product_id": "PRD-101",
                "effective_date": "2025-11-08",
                "base_rate": "250.00",
                "currency": "USD"
            }
        }
    }

    @field_validator("origin", "destination", "product_id", "surcharge_type", "currency", mode="before")
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


MODEL_REGISTRY = {
    "customer_ingest": Customer,
    "tracking_ingest": Tracking,
    "rate_ingest": RateTable,
}