-- ====================================================================
-- Demand Prediction & Food Waste Reduction Platform
-- 001_initial_schema.sql: Core PostgreSQL / Supabase Schema
-- ====================================================================

-- 1. Restaurants & Branches (Multi-Branch Support)
CREATE TABLE IF NOT EXISTS restaurants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    contact_email VARCHAR(255),
    currency VARCHAR(10) DEFAULT 'USD',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS branches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    city VARCHAR(100),
    timezone VARCHAR(50) DEFAULT 'UTC',
    opening_time TIME DEFAULT '09:00:00',
    closing_time TIME DEFAULT '23:00:00',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2. Menu Items & Ingredients
CREATE TABLE IF NOT EXISTS menu_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL, -- e.g. Main Course, Appetizer, Dessert, Beverage
    selling_price DECIMAL(10, 2) NOT NULL CHECK (selling_price >= 0),
    preparation_cost DECIMAL(10, 2) NOT NULL CHECK (preparation_cost >= 0),
    shelf_life_hours INT DEFAULT 24, -- Shelf life once prepared
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ingredients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL, -- Dairy, Meat, Produce, Dry Goods, Spices
    unit VARCHAR(50) NOT NULL, -- kg, g, liter, portions, count
    unit_cost DECIMAL(10, 2) NOT NULL CHECK (unit_cost >= 0),
    shelf_life_days INT DEFAULT 7,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Bill of Materials: Ingredients needed per portion of menu item
CREATE TABLE IF NOT EXISTS recipe_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    menu_item_id UUID NOT NULL REFERENCES menu_items(id) ON DELETE CASCADE,
    ingredient_id UUID NOT NULL REFERENCES ingredients(id) ON DELETE RESTRICT,
    quantity_required DECIMAL(10, 4) NOT NULL CHECK (quantity_required > 0),
    unit VARCHAR(50) NOT NULL,
    UNIQUE(menu_item_id, ingredient_id)
);

-- 3. Inventory Items & Stock Tracking
CREATE TABLE IF NOT EXISTS inventory_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    ingredient_id UUID NOT NULL REFERENCES ingredients(id) ON DELETE RESTRICT,
    current_stock DECIMAL(10, 2) NOT NULL DEFAULT 0 CHECK (current_stock >= 0),
    safety_stock DECIMAL(10, 2) NOT NULL DEFAULT 10 CHECK (safety_stock >= 0),
    reorder_point DECIMAL(10, 2) NOT NULL DEFAULT 20 CHECK (reorder_point >= 0),
    unit VARCHAR(50) NOT NULL,
    expiry_date DATE,
    last_restocked_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(branch_id, ingredient_id)
);

-- 4. Sales / Order Records (Historical & Streaming POS Ingestion)
CREATE TABLE IF NOT EXISTS sales_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    menu_item_id UUID NOT NULL REFERENCES menu_items(id) ON DELETE RESTRICT,
    sale_date DATE NOT NULL,
    sale_hour INT CHECK (sale_hour >= 0 AND sale_hour <= 23),
    quantity_sold INT NOT NULL CHECK (quantity_sold >= 0),
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0),
    total_amount DECIMAL(10, 2) NOT NULL CHECK (total_amount >= 0),
    promotion_active BOOLEAN DEFAULT FALSE,
    holiday_flag BOOLEAN DEFAULT FALSE,
    weather_temp DECIMAL(5, 2), -- Celsius
    rainfall_mm DECIMAL(6, 2) DEFAULT 0 CHECK (rainfall_mm >= 0),
    weather_condition VARCHAR(100), -- Clear, Rain, Overcast, Thunderstorm
    source VARCHAR(50) DEFAULT 'pos_batch', -- pos_realtime, pos_batch, manual, synthetic
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 5. Food Waste Tracking & Cause Analysis
CREATE TABLE IF NOT EXISTS waste_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    menu_item_id UUID NOT NULL REFERENCES menu_items(id) ON DELETE RESTRICT,
    record_date DATE NOT NULL,
    prepared_quantity INT NOT NULL CHECK (prepared_quantity >= 0),
    sold_quantity INT NOT NULL CHECK (sold_quantity >= 0),
    remaining_quantity INT NOT NULL CHECK (remaining_quantity >= 0),
    wasted_quantity INT NOT NULL CHECK (wasted_quantity >= 0),
    waste_percentage DECIMAL(5, 2) NOT NULL CHECK (waste_percentage >= 0 AND waste_percentage <= 100),
    waste_reason VARCHAR(100) NOT NULL, -- over_production, expired_shelf_life, preparation_error, customer_leftover, spoilage
    cost_wasted DECIMAL(10, 2) NOT NULL CHECK (cost_wasted >= 0),
    notes TEXT,
    corrective_action_recommended TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 6. Demand Predictions & Feedback Evaluations
CREATE TABLE IF NOT EXISTS demand_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    menu_item_id UUID NOT NULL REFERENCES menu_items(id) ON DELETE RESTRICT,
    target_date DATE NOT NULL,
    predicted_demand DECIMAL(10, 2) NOT NULL CHECK (predicted_demand >= 0),
    confidence_lower DECIMAL(10, 2) NOT NULL CHECK (confidence_lower >= 0),
    confidence_upper DECIMAL(10, 2) NOT NULL CHECK (confidence_upper >= confidence_lower),
    recommended_preparation INT NOT NULL CHECK (recommended_preparation >= 0),
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    feature_contributions JSONB, -- Explainability feature weights (e.g. {"weekend": +12.5, "rain": -4.2})
    actual_demand INT, -- Backfilled once sales arrive for ML feedback loop
    absolute_error DECIMAL(10, 2),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS model_evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    evaluation_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    dataset_period VARCHAR(100),
    sample_count INT NOT NULL,
    mae DECIMAL(10, 4) NOT NULL,
    rmse DECIMAL(10, 4) NOT NULL,
    mape DECIMAL(10, 4),
    r2_score DECIMAL(10, 4) NOT NULL,
    is_active_model BOOLEAN DEFAULT FALSE,
    notes TEXT
);

-- 7. Operational Alerts
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    alert_type VARCHAR(100) NOT NULL, -- high_waste_risk, stockout_risk, excess_inventory, expiry_warning, surge_demand
    severity VARCHAR(20) NOT NULL, -- info, warning, critical
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB,
    status VARCHAR(50) DEFAULT 'active', -- active, acknowledged, resolved
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMPTZ
);

-- 8. Surplus Food & Donation Tracking
CREATE TABLE IF NOT EXISTS surplus_donations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    menu_item_id UUID NOT NULL REFERENCES menu_items(id) ON DELETE RESTRICT,
    surplus_quantity INT NOT NULL CHECK (surplus_quantity > 0),
    unit VARCHAR(50) DEFAULT 'portions',
    food_safe_certified BOOLEAN NOT NULL DEFAULT FALSE,
    certified_by VARCHAR(255),
    certification_timestamp TIMESTAMPTZ,
    recipient_ngo VARCHAR(255),
    contact_phone VARCHAR(50),
    pickup_status VARCHAR(50) DEFAULT 'pending', -- pending, scheduled, picked_up, delivered, rejected
    impact_meals_saved INT DEFAULT 0,
    carbon_avoided_kg DECIMAL(10, 2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
