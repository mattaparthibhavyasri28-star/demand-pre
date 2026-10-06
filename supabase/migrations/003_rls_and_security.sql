-- ====================================================================
-- 003_rls_and_security.sql: Supabase Row Level Security (RLS) & Policies
-- ====================================================================

-- Enable RLS on core tables
ALTER TABLE restaurants ENABLE ROW LEVEL SECURITY;
ALTER TABLE branches ENABLE ROW LEVEL SECURITY;
ALTER TABLE menu_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE ingredients ENABLE ROW LEVEL SECURITY;
ALTER TABLE recipe_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE waste_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE demand_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_evaluations ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE surplus_donations ENABLE ROW LEVEL SECURITY;

-- Anonymous / Authenticated / Service Role Policies
-- Backend API uses Service Role key for elevated operational workflows
-- Read policies for authenticated restaurant staff:
CREATE POLICY "Allow authenticated read on restaurants"
    ON restaurants FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Allow authenticated read on branches"
    ON branches FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Allow authenticated read on menu_items"
    ON menu_items FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Allow authenticated read on sales_records"
    ON sales_records FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Allow authenticated read on waste_records"
    ON waste_records FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Allow authenticated read on demand_predictions"
    ON demand_predictions FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Allow authenticated read on alerts"
    ON alerts FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Allow authenticated read on surplus_donations"
    ON surplus_donations FOR SELECT
    TO authenticated
    USING (true);
