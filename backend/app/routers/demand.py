from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.entities import MenuItem
from backend.app.schemas.demand import (
    ItemPredictionRequest,
    ItemPredictionResponse,
    NearRealTimeUpdateRequest,
    NearRealTimeUpdateResponse,
    DailyForecastSummary
)
from backend.app.services.demand_forecasting import (
    forecast_single_item,
    update_prediction_near_real_time,
    get_loaded_model
)

router = APIRouter(prefix="/demand", tags=["Demand Forecasting"])

@router.post("/predict-item", response_model=ItemPredictionResponse)
def predict_item_demand(request: ItemPredictionRequest, db: Session = Depends(get_db)):
    return forecast_single_item(
        db=db,
        branch_id=request.branch_id,
        menu_item_id=request.menu_item_id,
        target_date=request.target_date,
        weather_temp=request.weather_temp or 25.0,
        rainfall_mm=request.rainfall_mm or 0.0,
        weather_condition=request.weather_condition or "Clear",
        promotion_active=request.promotion_active or False,
        holiday_flag=request.holiday_flag or False
    )

@router.get("/daily-forecast", response_model=DailyForecastSummary)
def get_daily_forecast(
    branch_id: str = Query(..., description="Branch identifier"),
    target_date: Optional[date] = Query(default=None, description="Forecast target date"),
    weather_condition: str = Query("Clear", description="Weather forecast condition"),
    rainfall_mm: float = Query(0.0, description="Forecast rainfall"),
    is_holiday: bool = Query(False, description="Holiday flag"),
    db: Session = Depends(get_db)
):
    if target_date is None:
        target_date = date.today()
        
    menu_items = db.query(MenuItem).filter(MenuItem.is_active == True).all()
    item_forecasts = []
    total_portions = 0.0
    
    for item in menu_items:
        f = forecast_single_item(
            db=db,
            branch_id=branch_id,
            menu_item_id=item.id,
            target_date=target_date,
            weather_condition=weather_condition,
            rainfall_mm=rainfall_mm,
            holiday_flag=is_holiday
        )
        item_forecasts.append(f)
        total_portions += f.predicted_demand
        
    return DailyForecastSummary(
        date=target_date,
        total_predicted_portions=round(total_portions, 1),
        items=item_forecasts
    )

@router.post("/near-real-time-update", response_model=NearRealTimeUpdateResponse)
def near_real_time_update(request: NearRealTimeUpdateRequest, db: Session = Depends(get_db)):
    return update_prediction_near_real_time(
        db=db,
        branch_id=request.branch_id,
        menu_item_id=request.menu_item_id,
        target_date=request.target_date,
        current_hour=request.current_hour,
        cumulative_sales=request.cumulative_sales_so_far,
        current_weather_condition=request.current_weather_condition or "Clear"
    )

@router.get("/model-metrics")
def get_model_metrics():
    model_artifact = get_loaded_model()
    return {
        "selected_model": model_artifact.get("model_name"),
        "version": model_artifact.get("version"),
        "metrics": model_artifact.get("metrics"),
        "all_candidate_metrics": model_artifact.get("all_candidate_metrics"),
        "feature_importances": model_artifact.get("feature_importances")
    }

@router.get("/backtest")
def get_operational_backtest(days: int = Query(90, ge=14, le=180)):
    from backend.app.ml.backtester import run_historical_operational_backtest
    return run_historical_operational_backtest(days_to_evaluate=days)
