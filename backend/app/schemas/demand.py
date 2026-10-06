from typing import Optional, List, Dict
from datetime import date, datetime
from pydantic import BaseModel, Field

class ExplainabilityFactor(BaseModel):
    factor_name: str
    impact_percentage: float
    description: str

class ItemPredictionRequest(BaseModel):
    branch_id: str
    menu_item_id: str
    target_date: date
    weather_temp: Optional[float] = 26.5
    rainfall_mm: Optional[float] = 0.0
    weather_condition: Optional[str] = "Clear"
    promotion_active: Optional[bool] = False
    holiday_flag: Optional[bool] = False

class ItemPredictionResponse(BaseModel):
    branch_id: str
    menu_item_id: str
    menu_item_name: str
    target_date: date
    predicted_demand: float
    confidence_lower: float
    confidence_upper: float
    recommended_preparation: int
    model_name: str
    model_version: str
    feature_contributions: List[ExplainabilityFactor] = []

class NearRealTimeUpdateRequest(BaseModel):
    branch_id: str
    menu_item_id: str
    target_date: date
    current_hour: int = Field(ge=0, le=23)
    cumulative_sales_so_far: int = Field(ge=0)
    current_weather_condition: Optional[str] = "Clear"
    is_lunch_rush_active: Optional[bool] = False

class NearRealTimeUpdateResponse(BaseModel):
    branch_id: str
    menu_item_id: str
    menu_item_name: str
    target_date: date
    current_hour: int
    initial_daily_prediction: float
    cumulative_sales_so_far: int
    updated_predicted_total: float
    remaining_predicted_sales: float
    recommended_additional_prep: int
    status_assessment: str # on_track, surging_demand, lagging_demand
    explanation: str

class DailyForecastSummary(BaseModel):
    date: date
    total_predicted_portions: float
    items: List[ItemPredictionResponse]
