from typing import Optional, List, Dict
from datetime import date, datetime
from pydantic import BaseModel, Field

class WasteLogCreate(BaseModel):
    branch_id: str
    menu_item_id: str
    record_date: date
    prepared_quantity: int = Field(ge=0)
    sold_quantity: int = Field(ge=0)
    remaining_quantity: int = Field(ge=0)
    wasted_quantity: int = Field(ge=0)
    waste_reason: str # over_production, expired_shelf_life, preparation_error, customer_leftover, spoilage
    notes: Optional[str] = None

class WasteRecordResponse(BaseModel):
    id: str
    branch_id: str
    menu_item_id: str
    menu_item_name: str
    record_date: date
    prepared_quantity: int
    sold_quantity: int
    remaining_quantity: int
    wasted_quantity: int
    waste_percentage: float
    waste_reason: str
    cost_wasted: float
    notes: Optional[str]
    corrective_action_recommended: Optional[str]
    created_at: datetime

class WasteCauseBreakdown(BaseModel):
    reason: str
    display_name: str
    quantity: int
    cost: float
    percentage_of_total_waste: float

class ActionableRecommendation(BaseModel):
    menu_item_id: str
    menu_item_name: str
    issue_detected: str
    recommended_action: str
    expected_savings_portions: int
    expected_cost_reduction: float

class WasteAnalyticsResponse(BaseModel):
    branch_id: str
    start_date: date
    end_date: date
    total_prepared: int
    total_sold: int
    total_wasted: int
    overall_waste_percentage: float
    total_cost_wasted: float
    cause_breakdown: List[WasteCauseBreakdown]
    actionable_recommendations: List[ActionableRecommendation]
    recent_logs: List[WasteRecordResponse]
