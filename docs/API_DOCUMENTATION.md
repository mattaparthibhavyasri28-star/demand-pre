# API Documentation

The backend exposes a REST API powered by FastAPI at prefix `/api/v1`.
Interactive Swagger UI is available at `/docs` and ReDoc at `/redoc`.

---

## Endpoint Reference

### 1. System Health
- **`GET /api/v1/health`**
  - Returns backend and database health status, timestamp, and environment.

### 2. Restaurants & Branches
- **`GET /api/v1/branches`**
  - Lists all configured restaurant branches.
- **`GET /api/v1/branches/{branch_id}/menu`**
  - Lists active menu items catalog for the branch.

### 3. Demand Forecasting
- **`POST /api/v1/demand/predict-item`**
  - Predicts demand for a specific item on a target date with weather and holiday parameters.
  - Returns predicted demand, 95% confidence intervals, recommended prep, and explainability factors.
- **`GET /api/v1/demand/daily-forecast`**
  - Query params: `branch_id`, `target_date`, `weather_condition`, `rainfall_mm`, `is_holiday`.
  - Returns daily summary across all active menu items.
- **`POST /api/v1/demand/near-real-time-update`**
  - Intra-day updating endpoint. Accepts `current_hour` and `cumulative_sales_so_far`.
  - Returns updated full-day forecast, remaining sales, and recommended additional prep batch.
- **`GET /api/v1/demand/model-metrics`**
  - Returns empirical validation metrics (MAE, RMSE, MAPE, R²) and feature importances for all candidate models.

### 4. Smart Inventory Management
- **`GET /api/v1/inventory/recommendations`**
  - Query params: `branch_id`, `planning_date`.
  - Returns raw ingredient consumption, safety stock thresholds (Z=1.65), reorder points, net deficits, and purchase quantities.
- **`GET /api/v1/inventory/items`**
  - Query params: `branch_id`.
  - Returns inventory items, current stock, and expiry dates.

### 5. Food Waste Tracking & Cause Analysis
- **`POST /api/v1/waste/log`**
  - Records shift kitchen waste (prepared, sold, remaining, wasted, reason, notes).
- **`GET /api/v1/waste/analytics`**
  - Query params: `branch_id`, `start_date`, `end_date`.
  - Returns waste %, cost wasted, root-cause breakdown (`over_production`, `expired_shelf_life`, etc.), and actionable chef feedback recommendations.

### 6. What-If Scenario Simulation
- **`POST /api/v1/simulation/what-if`**
  - Simulates operational scenarios (heavy rain, holidays, active promotions, demand shifts).
  - Returns simulated demand vs baseline, net % change, waste risk portions, and key driver explanations.

### 7. Operational Alerts
- **`GET /api/v1/alerts`**
  - Query params: `branch_id`. Returns active risk alerts.
- **`POST /api/v1/alerts/{alert_id}/acknowledge`**
  - Acknowledges or resolves an operational alert.

### 8. Surplus Food & NGO Donations
- **`GET /api/v1/donations/surplus-candidates`**
  - Detects unsold clean surplus portions from recent shifts.
- **`POST /api/v1/donations/certify-and-dispatch`**
  - Registers food-safety verified donation (temperature check, visual check, packaging integrity, certified by staff).
- **`GET /api/v1/donations`**
  - Returns donation logistics history and pickup statuses.

### 9. Sustainability & ESG Impact
- **`GET /api/v1/sustainability/summary`**
  - Query params: `branch_id`, `days`.
  - Returns meals saved, money saved, estimated CO2e avoided (kg), and water preserved (Liters).

### 10. POS Integration
- **`POST /api/v1/pos/upload-csv`**
  - Uploads sales spreadsheet (multipart CSV).
- **`POST /api/v1/pos/webhook`**
  - Accepts live POS event streaming payloads from external registers.
- **`POST /api/v1/pos/batch-ingest`**
  - Ingests batch JSON transactions.
