-- ====================================================================
-- 002_indexes_and_constraints.sql: Performance Indexes & Constraints
-- ====================================================================

-- 1. Sales & POS Ingestion Indexes
CREATE INDEX IF NOT EXISTS idx_sales_branch_date ON sales_records(branch_id, sale_date DESC);
CREATE INDEX IF NOT EXISTS idx_sales_item_date ON sales_records(menu_item_id, sale_date DESC);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales_records(sale_date);

-- 2. Waste Records Indexes
CREATE INDEX IF NOT EXISTS idx_waste_branch_date ON waste_records(branch_id, record_date DESC);
CREATE INDEX IF NOT EXISTS idx_waste_reason ON waste_records(waste_reason);
CREATE INDEX IF NOT EXISTS idx_waste_item ON waste_records(menu_item_id);

-- 3. Demand Prediction & Feedback Loop Indexes
CREATE INDEX IF NOT EXISTS idx_predictions_branch_date ON demand_predictions(branch_id, target_date DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_item_date ON demand_predictions(menu_item_id, target_date DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_model ON demand_predictions(model_name, model_version);

-- 4. Inventory Tracking Indexes
CREATE INDEX IF NOT EXISTS idx_inventory_branch ON inventory_items(branch_id);
CREATE INDEX IF NOT EXISTS idx_inventory_expiry ON inventory_items(expiry_date);

-- 5. Operational Alerts & Surplus Indexes
CREATE INDEX IF NOT EXISTS idx_alerts_branch_status ON alerts(branch_id, status);
CREATE INDEX IF NOT EXISTS idx_donations_status ON surplus_donations(pickup_status);
