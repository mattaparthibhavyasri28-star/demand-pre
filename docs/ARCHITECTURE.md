# Architecture Documentation

## Demand Prediction for Food Wastage Reduction in Restaurants

### 1. Executive Summary

EcoKitchen AI is an integrated, closed-loop decision-support platform designed for restaurant managers, kitchen chefs, and inventory teams. Rather than treating demand prediction in isolation, the system connects forecasting directly to operational prep decisions, inventory purchase calculations, waste cause tracking, surplus food redistribution, and model retraining.

### 2. High-Level Closed-Loop Flow

```text
Historical Sales Data (POS/CSV)
       +
Weather Factors (Temp, Rainfall, Conditions)
       +
Calendar Context (Day of Week, Holidays, Festivals)
       +
Active Promotions & Pricing
       ↓
Demand Prediction Engine (XGBoost Regressor)
       ↓
Kitchen Preparation Recommendation (+95% Confidence Bounds)
       ↓
Inventory Purchase Reorder Engine (BOM Explosion + Safety Stock)
       ↓
Intra-Day Sales Monitoring (Near-Real-Time Updating)
       ↓
Kitchen Shift Waste Logging (Root-Cause Breakdown)
       ↓
Surplus Food Redistribution (Food-Safety Check & NGO Dispatch)
       ↓
Sustainability Accounting (CO2e, Water, Cost Savings)
       ↓
ML Feedback Loop (Bias & Error Evaluation -> Auto-Calibrated Prep Multipliers)
```

### 3. Component Architecture

```text
┌────────────────────────────────────────────────────────┐
│              Next.js 14 Frontend (App Router)          │
│   Overview | Forecast | Inventory | Waste | Simulation │
│   Surplus & Donations | Sustainability | POS | Alerts   │
└───────────────────────────┬────────────────────────────┘
                            │ REST / JSON
┌───────────────────────────▼────────────────────────────┐
│                  FastAPI Python Backend                │
│  - /api/v1/demand         - /api/v1/inventory          │
│  - /api/v1/waste          - /api/v1/simulation         │
│  - /api/v1/alerts         - /api/v1/donations          │
│  - /api/v1/sustainability - /api/v1/pos                │
└──────────────┬──────────────────────────┬──────────────┘
               │                          │
┌──────────────▼─────────────┐ ┌──────────▼──────────────┐
│       ML & Analytics       │ │  Supabase PostgreSQL /  │
│ - Feature Pipeline         │ │      SQLite Engine      │
│ - Comparative Models       │ │ - Normalized Schema     │
│ - Explainability (XAI)     │ │ - Foreign Keys & RLS    │
│ - ML Feedback Loop         │ │ - Audit & Performance   │
└────────────────────────────┘ └─────────────────────────┘
```

### 4. Authoritative Responsibilities
- **Frontend (Next.js + TypeScript)**: Responsive UI, forms, interactive sliders, chart visualizations, scenario inputs, and validation feedback.
- **Backend (Python / FastAPI)**: Authoritative for all business logic, BOM explosions, safety stock calculations, ML inference, explainability attribution, and database operations.
- **Database (Supabase PostgreSQL / SQLAlchemy)**: ACID compliance, referential constraints, indexing on date/branch/item keys, and Row Level Security (RLS).
