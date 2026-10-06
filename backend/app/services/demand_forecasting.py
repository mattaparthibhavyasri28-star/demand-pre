"""
Demand Forecasting Service
--------------------------
Handles model inference, confidence intervals, near-real-time intra-day updates,
and explainability factor generation for menu items.
"""

from typing import List, Dict, Any, Optional
from datetime import date
from pathlib import Path
import joblib
import numpy as np
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.models.entities import MenuItem, SalesRecord, DemandPrediction
from backend.app.schemas.demand import (
    ItemPredictionResponse,
    ExplainabilityFactor,
    NearRealTimeUpdateResponse
)
from backend.app.ml.feature_pipeline import build_single_inference_vector
from backend.app.ml.explainability import explain_prediction
from backend.app.ml.feedback_loop import evaluate_recent_prediction_bias

_MODEL_CACHE = None

def get_loaded_model() -> Dict[str, Any]:
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        model_file = settings.TRAINED_MODELS_DIR / "best_model.joblib"
        if not model_file.exists():
            # Trigger quick training if not yet run
            from backend.app.ml.model_trainer import train_and_evaluate_all_models
            train_and_evaluate_all_models()
        _MODEL_CACHE = joblib.load(model_file)
    return _MODEL_CACHE

def forecast_single_item(
    db: Session,
    branch_id: str,
    menu_item_id: str,
    target_date: date,
    weather_temp: float = 25.0,
    rainfall_mm: float = 0.0,
    weather_condition: str = "Clear",
    promotion_active: bool = False,
    holiday_flag: bool = False,
    festival_flag: bool = False
) -> ItemPredictionResponse:
    item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
    item_name = item.name if item else "Menu Item"
    item_price = item.selling_price if item else 12.0
    
    # Query recent sales history for lag features
    recent_sales = (
        db.query(SalesRecord.quantity_sold)
        .filter(
            SalesRecord.branch_id == branch_id,
            SalesRecord.menu_item_id == menu_item_id
        )
        .order_by(SalesRecord.sale_date.desc())
        .limit(14)
        .all()
    )
    sales_history = [s[0] for s in reversed(recent_sales)] if recent_sales else []
    
    # Build feature vector
    x_vec = build_single_inference_vector(
        menu_item_id=menu_item_id,
        target_date=target_date,
        unit_price=item_price,
        promotion_active=promotion_active,
        holiday_flag=holiday_flag,
        festival_flag=festival_flag,
        weather_temp=weather_temp,
        rainfall_mm=rainfall_mm,
        recent_sales_history=sales_history
    )
    
    model_artifact = get_loaded_model()
    model = model_artifact["model"]
    model_name = model_artifact.get("model_name", "XGBoost")
    model_version = model_artifact.get("version", "1.0.0")
    rmse = model_artifact.get("metrics", {}).get("rmse", 7.0)
    
    raw_pred = float(model.predict(x_vec)[0])
    raw_pred = max(5.0, raw_pred)
    
    # Check closed-loop ML feedback bias
    bias_info = evaluate_recent_prediction_bias(db, branch_id, menu_item_id)
    adj_pred = raw_pred * bias_info.get("feedback_multiplier", 1.0)
    
    # Uncertainty confidence interval: 95% interval using empirical standard error (1.96 * RMSE)
    margin = 1.96 * (rmse * 0.7) # item-level conditioned std error
    conf_lower = max(2.0, round(adj_pred - margin, 1))
    conf_upper = round(adj_pred + margin, 1)
    
    # Recommended kitchen prep: adjusted prediction rounded up to whole portion
    recommended_prep = int(np.ceil(adj_pred))
    
    # Explainability factors
    day_of_week = target_date.weekday()
    is_weekend = day_of_week in [4, 5, 6]
    base_demand = np.mean(sales_history) if sales_history else 50.0
    factors = explain_prediction(
        base_demand=base_demand,
        predicted_demand=adj_pred,
        is_weekend=is_weekend,
        promotion_active=promotion_active,
        holiday_flag=holiday_flag,
        festival_flag=festival_flag,
        rainfall_mm=rainfall_mm,
        weather_temp=weather_temp,
        weather_condition=weather_condition,
        item_name=item_name
    )
    
    return ItemPredictionResponse(
        branch_id=branch_id,
        menu_item_id=menu_item_id,
        menu_item_name=item_name,
        target_date=target_date,
        predicted_demand=round(adj_pred, 1),
        confidence_lower=conf_lower,
        confidence_upper=conf_upper,
        recommended_preparation=recommended_prep,
        model_name=model_name,
        model_version=model_version,
        feature_contributions=factors
    )

def update_prediction_near_real_time(
    db: Session,
    branch_id: str,
    menu_item_id: str,
    target_date: date,
    current_hour: int,
    cumulative_sales: int,
    current_weather_condition: str = "Clear"
) -> NearRealTimeUpdateResponse:
    """
    Near-Real-Time Demand Updating:
    Updates daily forecast as actual sales accumulate throughout the day.
    Uses typical diurnal sales curve (e.g. 15% by 12:00, 45% by 14:00, 75% by 20:00).
    """
    item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
    item_name = item.name if item else "Menu Item"
    
    # Baseline forecast
    base_forecast = forecast_single_item(
        db, branch_id, menu_item_id, target_date, weather_condition=current_weather_condition
    )
    initial_total = base_forecast.predicted_demand
    
    # Diurnal hourly cumulative distribution curve for restaurant dining
    hourly_distribution = {
        9: 0.02, 10: 0.05, 11: 0.10, 12: 0.22, 13: 0.42, 14: 0.52,
        15: 0.57, 16: 0.60, 17: 0.65, 18: 0.72, 19: 0.84, 20: 0.93,
        21: 0.98, 22: 1.00, 23: 1.00
    }
    
    expected_fraction = hourly_distribution.get(current_hour, min(1.0, max(0.05, current_hour / 22.0)))
    expected_so_far = initial_total * expected_fraction
    
    # Bayesian / Exponential updating: blend historical expectation with current day pace
    if expected_fraction > 0.10:
        pace_ratio = cumulative_sales / max(1.0, expected_so_far)
        # Dampen extreme early morning noise
        pace_weight = min(0.75, expected_fraction * 0.9)
        updated_total = (initial_total * (1.0 - pace_weight)) + ((cumulative_sales / expected_fraction) * pace_weight)
    else:
        updated_total = initial_total
        pace_ratio = 1.0
        
    updated_total = max(float(cumulative_sales), round(updated_total, 1))
    remaining_sales = max(0.0, round(updated_total - cumulative_sales, 1))
    
    if pace_ratio > 1.15:
        status = "surging_demand"
        explanation = f"Sales pace is running +{round((pace_ratio - 1.0) * 100)}% above baseline. Recommending supplemental preparation to avoid dinner stock-out."
        prep_adj = int(np.ceil(remaining_sales * 1.05))
    elif pace_ratio < 0.85 and current_hour >= 14:
        status = "lagging_demand"
        explanation = f"Afternoon sales are tracking -{round((1.0 - pace_ratio) * 100)}% below expectation. Cease further batch prep to prevent over-production waste."
        prep_adj = int(np.floor(remaining_sales * 0.90))
    else:
        status = "on_track"
        explanation = "Order pace aligns with historical diurnal trajectory. Maintain standard prep schedule."
        prep_adj = int(np.ceil(remaining_sales))
        
    return NearRealTimeUpdateResponse(
        branch_id=branch_id,
        menu_item_id=menu_item_id,
        menu_item_name=item_name,
        target_date=target_date,
        current_hour=current_hour,
        initial_daily_prediction=initial_total,
        cumulative_sales_so_far=cumulative_sales,
        updated_predicted_total=updated_total,
        remaining_predicted_sales=remaining_sales,
        recommended_additional_prep=prep_adj,
        status_assessment=status,
        explanation=explanation
    )
