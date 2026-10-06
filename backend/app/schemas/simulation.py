from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field

class WhatIfSimulationRequest(BaseModel):
    branch_id: str
    target_date: date
    weather_scenario: str = "Clear" # Clear, Heavy Rain, Heatwave, Cold Snap
    temperature_override: Optional[float] = None
    rainfall_override: Optional[float] = None
    is_holiday: bool = False
    is_festival: bool = False
    active_promotion: bool = False
    demand_shift_percentage: float = 0.0 # e.g. +15.0 or -10.0

class SimulatedItemResult(BaseModel):
    menu_item_id: str
    menu_item_name: str
    baseline_demand: float
    simulated_demand: float
    demand_change_percentage: float
    recommended_preparation: int
    predicted_waste_risk_portions: int
    risk_level: str # low, moderate, high

class WhatIfSimulationResponse(BaseModel):
    branch_id: str
    target_date: date
    scenario_description: str
    total_baseline_demand: float
    total_simulated_demand: float
    net_demand_change_pct: float
    total_estimated_waste_risk: int
    key_drivers: List[str]
    item_simulations: List[SimulatedItemResult]
    disclaimer: str = "Predictions represent what-if estimates for decision-support and scenario planning, not guaranteed outcomes."
