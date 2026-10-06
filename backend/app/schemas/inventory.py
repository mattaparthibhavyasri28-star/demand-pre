from typing import Optional, List
from datetime import date
from pydantic import BaseModel

class IngredientRequirement(BaseModel):
    ingredient_id: str
    ingredient_name: str
    category: str
    unit: str
    unit_cost: float
    current_stock: float
    predicted_demand_consumption: float
    safety_stock: float
    reorder_point: float
    net_deficit: float
    recommended_purchase: float
    estimated_purchase_cost: float
    urgency: str # normal, reorder_needed, critical_stockout

class PurchaseRecommendationResponse(BaseModel):
    branch_id: str
    planning_date: date
    total_estimated_purchase_cost: float
    items_requiring_reorder: int
    recommendations: List[IngredientRequirement]
    methodology_notes: str
