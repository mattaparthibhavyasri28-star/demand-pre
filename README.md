# Demand Prediction for Food Wastage Reduction in Restaurants

A local, offline-first B.Tech IT project that learns from restaurant sales history, compares regression models, forecasts future item demand, and provides simple, explainable food-preparation guidance. The Streamlit application uses no API keys or external APIs.

## Project objective

Predict portions sold for a selected menu item and meal using historical restaurant sales. Compare preparation plans with the model forecast, estimate possible excess food, and give staff a transparent Python rule-based suggestion to reduce or increase preparation.

## Features

- Upload a CSV or use the bundled demonstration sales dataset.
- Validate and clean date, category, price, sales, and customer fields; summarize removed rows.
- Explore daily, menu-item, and weekday sales.
- Build day, month, weekend, price, meal/item, prior-sales, prior-week sales, rolling-sales, prior-customer, and holiday/event features.
- Train and compare Linear Regression, Decision Tree, Random Forest, and Gradient Boosting.
- Use a chronological holdout and report MAE, MSE, RMSE, and R².
- Forecast a future item/meal and compare with planned preparation.
- Estimate excess food and excess percentage; explain a reduce/maintain/increase recommendation.
- View holdout actual-vs-predicted charts and download prediction results as CSV.
- Save the selected trained model locally; no remote inference is used.

## Technology used

- Python **3.11.x** (required project environment)
- Streamlit, Pandas, NumPy, scikit-learn, Matplotlib, Seaborn, SciPy, and Joblib
- CSV files for local data and a local pickle model artifact

No database, LLM, cloud account, API key, POS connection, weather service, or other external API is required by the Streamlit application.

## Project structure

```text
food_waste_prediction/
├── app.py
├── data/
│   └── restaurant_sales.csv
├── models/                    # Created locally after model training
├── src/
│   ├── data_preprocessing.py
│   ├── feature_engineering.py
│   ├── train_model.py
│   ├── prediction.py
│   └── recommendations.py
├── requirements.txt
└── README.md
```

This repository also retains earlier `backend/`, `frontend/`, `supabase/`, and `docs/` work. The root `app.py` is the standalone Streamlit application. Run that file for the offline workflow described here.

## Dataset requirements

Required CSV columns:

| Column | Meaning |
|---|---|
| `date` | Sales date parseable by Pandas |
| `menu_item` | Dish/item name |
| `meal_type` | Breakfast, lunch, dinner, or service label |
| `price` | Positive unit price |
| `quantity_sold` | Non-negative portions sold (prediction target) |
| `customers` | Non-negative customer count |

Optional columns: `prepared_quantity` (used for estimated excess/waste analysis) and `holiday_event` (true/false indicator). Invalid dates, missing labels, invalid prices, and negative/missing counts are removed. Duplicate date/item/meal records keep the last row. At least eight daily records per item/meal are needed for lag features; more history is recommended.

The bundled CSV contains 6,570 **synthetic demonstration records** spanning six menu items and three meal types. It is generated for offline development, not collected from a real restaurant. Replace it with an authorized restaurant export before using recommendations operationally. Do not present demo metrics as real-world results.

## Workflow

1. Load the bundled CSV or upload a restaurant CSV.
2. Clean and validate records.
3. Explore sales by date, menu item, and weekday.
4. Create calendar and historical lag features using prior observations only.
5. Train Linear Regression, Decision Tree, Random Forest, and Gradient Boosting models.
6. Compare models on a chronological holdout using MAE, MSE, RMSE, and R².
7. Save the selected model locally to `models/demand_model.pkl`.
8. Forecast a future date and compare the result with planned preparation.
9. Download a prediction or validation set as CSV.

To train and save the model without opening the dashboard (after installing dependencies), run `python -m src.train_model`. The dashboard also trains automatically when the selected dataset changes.

The preparation rule is deterministic and explainable. Estimated excess is `max(0, prepared quantity − predicted demand)`; the corresponding percentage uses prepared quantity as its denominator. These are planning estimates, not measured waste. The app does not currently provide calibrated uncertainty intervals, live POS updates, reservations, weather, local-event feeds, or ingredient purchasing plans.

## Model training and evaluation

Each model fits on earlier dates and is evaluated on a later 20% date holdout. Historical sales/customer features are shifted so each row uses only earlier observations. Preprocessing and categorical encoding are fitted inside each model pipeline on its training partition. The model with the lowest holdout MAE is saved to `models/demand_model.pkl`.

- **MAE:** average absolute error in portions; lower is better.
- **MSE:** average squared error; lower is better and large errors are weighted more.
- **RMSE:** square root of MSE in portions; lower is better.
- **R²:** variance explained relative to a mean baseline; closer to 1 is better, and it can be negative.

Metrics are dataset-specific. A synthetic-data score is not evidence of expected restaurant performance.

## Install and run

Python **3.11.x is required**. Install Python 3.11 locally and ensure the Python Launcher can find it. From this directory:

```bash
py -3.11 -m venv .venv
```

Activate the environment:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies and start the app:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py
```

On macOS/Linux, create the environment with `python3.11 -m venv .venv` and activate with `source .venv/bin/activate`. Internet access is needed only to install packages. Once dependencies are installed, the application runs locally without API keys or external services.

## Project limitations

- Demo data is synthetic and does not establish real-world forecast accuracy or waste reduction.
- The selected model produces a point estimate; calibrated low/expected/high prediction ranges are not implemented.
- Future price and customer context use recent historical values; sudden changes require updated sales data.
- Lag features assume regular daily rows for each item/meal. Missing trading days should be represented consistently in the imported data.
- The excess calculation is an estimate based on planned portions minus predicted demand, not a measured waste log. The current UI's planned-preparation input is user supplied.
- The project does not currently integrate POS, reservation, delivery, inventory, supplier, weather, or event APIs.
- Python 3.11 runtime/model training/Streamlit checks must be completed in a local Python 3.11 environment before presenting it as verified.

## Future scope

- Validate with real restaurant data and rolling-origin backtests.
- Add calibrated prediction intervals and item-level uncertainty coverage checks.
- Add verified meal/service history, stockout flags, and actual waste logging.
- Support recipe-based ingredient purchasing and expiry-aware stock planning.
- Add optional, locally configured data imports if needed; preserve offline operation and staff approval of recommendations.

## Validation notes

Model evaluation uses an ordered date split: earlier records are used for training and later records for validation. Lag and rolling features are shifted so they only use prior sales. Validation metrics describe the supplied dataset only. A representative pilot requires real sales and preparation records collected over a suitable period.
