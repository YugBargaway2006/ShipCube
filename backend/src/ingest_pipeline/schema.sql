CREATE EXTENSION IF NOT EXISTS "pgcrypto";


-- ------------------------------
-- 1. customers
-- ------------------------------

CREATE TABLE customers (
    customer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_name TEXT NOT NULL,
    contact_email TEXT UNIQUE,
    account_tier VARCHAR(20) DEFAULT 'visitor' 
        CHECK (account_tier IN ('visitor', 'client')),
    created_at TIMESTAMPTZ DEFAULT (NOW())
);


-- ------------------------------
-- 2. customer_contracts
-- ------------------------------

-- CREATE TABLE customer_contracts (
--     contract_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--     customer_id UUID NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
--     contract_details JSONB,
--     effective_date DATE NOT NULL,
--     expiration_date DATE,
--     last_updated TIMESTAMPTZ DEFAULT (NOW())
-- );

-- CREATE INDEX idx_contract_customer_id ON customer_contracts(customer_id);


-- ------------------------------
-- 3. tracking
-- ------------------------------

CREATE TABLE tracking (
    order_id TEXT PRIMARY KEY,
    user_id TEXT,
    merchant_name TEXT,
    customer_name TEXT,
    transaction_status VARCHAR(50),
    transaction_type VARCHAR(50),
    invoice_number TEXT,
    transaction_date TIMESTAMPTZ,
    store_order_id TEXT,
    tracking_id TEXT,
    fulfillment_without_surcharge BOOLEAN,
    surcharge_applied BOOLEAN,
    invoice_amount NUMERIC(10,2),
    wms_fuel_surcharge NUMERIC(10,2),
    delivery_area_surcharge NUMERIC(10,2),
    address_correction NUMERIC(10,2),
    insurance_amount NUMERIC(10,2),
    final_invoice_amt NUMERIC(10,2),
    products_sold TEXT,
    total_quantity INT,
    ship_option_id TEXT,
    carrier TEXT,
    carrier_service TEXT,
    zone_used TEXT,
    actual_weight_oz NUMERIC(10,2),
    dim_weight_oz NUMERIC(10,2),
    billable_weight_oz NUMERIC(10,2),
    length NUMERIC(10,2),
    width NUMERIC(10,2),
    height NUMERIC(10,2),
    zip_code TEXT,
    city TEXT,
    destination_country TEXT,
    order_insert_timestamp TIMESTAMPTZ,
    label_generation_timestamp TIMESTAMPTZ,
    fc_name TEXT,
    order_category TEXT,
    final_invoice_amt_added_50c NUMERIC(10,2),
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    customer_id UUID REFERENCES customers(customer_id) ON DELETE SET NULL
);

CREATE INDEX idx_tracking_customer_id ON tracking(customer_id);
CREATE INDEX idx_tracking_status ON tracking(transaction_status);
CREATE INDEX idx_tracking_tracking_id ON tracking(tracking_id);


-- ------------------------------
-- 4. rate_table
-- ------------------------------

CREATE TABLE rate_table (
    route_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    effective_date DATE NOT NULL,
    base_rate NUMERIC(10, 2) NOT NULL,
    surcharge_type VARCHAR(50),
    surcharge_value NUMERIC(10, 2),
    currency CHAR(3) NOT NULL,
    last_updated TIMESTAMPTZ DEFAULT (NOW())
);

CREATE UNIQUE INDEX idx_rate_lookup 
    ON rate_table(origin, destination, product_id, effective_date);
