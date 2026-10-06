from typing import List, Dict
from datetime import date
from pydantic import BaseModel

class EnvironmentalFactor(BaseModel):
    category: str
    amount_saved: float
    unit: str
    methodology: str

class SustainabilitySummary(BaseModel):
    branch_id: str
    reporting_period: str
    total_food_prepared_portions: int
    total_food_sold_portions: int
    total_food_wasted_portions: int
    waste_percentage: float
    estimated_meals_diverted_from_landfill: int
    estimated_cost_saved_usd: float
    meals_donated_to_ngos: int
    estimated_co2e_avoided_kg: float
    estimated_water_saved_liters: float
    trend_waste_reduction_pct: float
    environmental_factors: List[EnvironmentalFactor]
    methodology_statement: str = "Environmental savings are model-estimated based on USDA & WRI life-cycle analysis factors (~2.5 kg CO2e / kg food, 1000L water / kg food) and decision-support data, not direct field measurements."
