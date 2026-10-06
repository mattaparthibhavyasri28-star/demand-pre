# Requirement Evidence Matrix

| Requirement | Priority | Implementation Module | Validation Method | Actual Evidence | Result |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Demand Prediction** | P0 | `backend/app/ml/model_trainer.py`, `backend/app/services/demand_forecasting.py` | Pytest test suite & Live REST query | XGBoost R² = 0.9328, MAE = 5.16 portions on 438 holdout test samples | **PASS** |
| **Weather-Aware Prediction** | P0 | `backend/app/ml/feature_pipeline.py`, `backend/app/routers/demand.py` | `test_services.py`, test_feature_pipeline | Rainfall mm & temperature parsed and tested; impact reflected in forecast | **PASS** |
| **Holiday / Event Awareness** | P0 | `backend/app/ml/feature_pipeline.py`, `backend/app/ml/explainability.py` | Unit & API tests | Holiday/festival flags drive forecast surge and explainability attribution | **PASS** |
| **Item-Level Forecasting with Uncertainty** | P0 | `backend/app/services/demand_forecasting.py`, `frontend/src/app/forecast/page.tsx` | `test_services.py`, Next.js build | Item-level forecasts with 95% CI bounds (`confidence_lower <= confidence_upper`) verified | **PASS** |
| **Smart Inventory Management** | P0 | `backend/app/services/inventory_optimizer.py`, `frontend/src/app/inventory/page.tsx` | `test_inventory.py` | Formula `Purchase = max(0, Demand + Safety - Current)` with Z=1.65 verified | **PASS** |
| **Food Waste Tracking** | P0 | `backend/app/services/waste_analyzer.py`, `backend/app/routers/waste.py` | `test_waste_analysis.py` | Shift log recorded, waste percentage calculated, database persisted | **PASS** |
| **Waste Cause Analysis** | P0 | `backend/app/services/waste_analyzer.py`, `frontend/src/app/waste/page.tsx` | `test_waste_analysis.py` | Decomposition across over_production, expired_shelf_life, prep_error, leftovers verified | **PASS** |
| **Near-Real-Time Intra-Day Updating** | P1 | `backend/app/services/demand_forecasting.py`, `frontend/src/app/forecast/page.tsx` | `test_near_real_time_updating` | Diurnal curve Bayesian update verified for lagging and surging sales | **PASS** |
| **Explainable AI (XAI)** | P1 | `backend/app/ml/explainability.py`, `backend/app/routers/demand.py` | `test_services.py`, Frontend UI | Transparent percentage impact and descriptions returned for each prediction | **PASS** |
| **What-If Scenario Simulation** | P1 | `backend/app/services/what_if_simulator.py`, `frontend/src/app/simulation/page.tsx` | `test_what_if_simulator` | Weather shocks, holidays, promotions simulated with waste risk scores | **PASS** |
| **Automatic Operational Alerts** | P1 | `backend/app/services/alert_engine.py`, `frontend/src/app/alerts/page.tsx` | `test_operational_alert_engine` | Data-derived triggers for waste risk, stockout, and expiry verified | **PASS** |
| **Sustainability Dashboard** | P1 | `backend/app/services/sustainability_calc.py`, `frontend/src/app/sustainability/page.tsx` | `test_sustainability_metrics` | Documented CO2e (2.5 kg/kg) & water (1000L/kg) LCA calculations verified | **PASS** |
| **Surplus Food & NGO Donation Workflow** | P1 | `backend/app/services/donation_workflow.py`, `frontend/src/app/donations/page.tsx` | `test_donation_workflow_and_safety_gate` | Surplus detection + mandatory human food safety checkpoint verified | **PASS** |
| **POS Integration (P2)** | P2 | `backend/app/routers/pos_integration.py`, `frontend/src/app/pos/page.tsx` | API endpoints & UI | CSV file upload parser and live POS webhook event simulator verified | **PASS** |
| **Database Migrations** | P0 | `supabase/migrations/` (001, 002, 003) | SQL validation | Complete normalized schema, indexes, constraints, and RLS policies created | **PASS** |
| **Frontend Compilation & Types** | P0 | `frontend/` Next.js 14 App Router + TypeScript | `next build` | 12/12 static pages built successfully with zero type or lint errors | **PASS** |
| **End-to-End REST Integration** | P0 | Next.js ↔ FastAPI ↔ Supabase / SQLite | Live HTTP verification | End-to-end queries returned 200 OK across all primary modules | **PASS** |
