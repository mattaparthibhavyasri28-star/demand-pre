"""
What-If Scenario Simulation Engine
-----------------------------------
Simulates operational and demand impacts of environmental and commercial scenarios:
e.g. Heavy Rain, Heatwave, Festival Days, Active Promotional Campaigns, or Demand Shifts.
"""

from typing import List
from datetime import date
from sqlalchemy.orm import Session

from backend.app.models.entities import MenuItem
from backend.app.schemas.simulation import (
    WhatIfSimulationRequest,
    WhatIfSimulationResponse,
    SimulatedItemResult
)
from backend.app.services.demand_forecasting import forecast_single_item

def run_what_if_simulation(
    db: Session,
    request: WhatIfSimulationRequest
) -> WhatIfSimulationResponse:
    menu_items = db.query(MenuItem).filter(MenuItem.is_active == True).all()
    
    # Weather scenario parameters
    rainfall = request.rainfall_override
    temp = request.temperature_override
    
    if rainfall is None:
        if request.weather_scenario == "Heavy Rain":
            rainfall = 28.0
        elif request.weather_scenario == "Light Rain":
            rainfall = 4.0
        else:
            rainfall = 0.0
            
    if temp is None:
        if request.weather_scenario == "Heatwave":
            temp = 36.0
        elif request.weather_scenario == "Cold Snap":
            temp = 12.0
        else:
            temp = 25.0
            
    key_drivers = []
    if rainfall > 15.0:
        key_drivers.append("Heavy rainfall (+28mm) triggers delivery preference & suppresses walk-in dining.")
    if request.is_festival:
        key_drivers.append("Festival calendar spike (+20-35% demand increase across group meals).")
    if request.is_holiday:
        key_drivers.append("Public holiday leisure dining boost.")
    if request.active_promotion:
        key_drivers.append("Active promotional campaign boost (+18% order velocity).")
    if abs(request.demand_shift_percentage) > 0.1:
        key_drivers.append(f"Manual demand sensitivity stress-test ({request.demand_shift_percentage:+.1f}%).")
        
    if not key_drivers:
        key_drivers.append("Standard operational baseline with neutral environmental factors.")
        
    sim_items: List[SimulatedItemResult] = []
    total_baseline = 0.0
    total_simulated = 0.0
    total_waste_risk = 0
    
    for item in menu_items:
        # 1. Baseline forecast (clear weather, no promos, no holidays)
        base_res = forecast_single_item(
            db=db,
            branch_id=request.branch_id,
            menu_item_id=item.id,
            target_date=request.target_date,
            weather_temp=24.0,
            rainfall_mm=0.0,
            weather_condition="Clear",
            promotion_active=False,
            holiday_flag=False,
            festival_flag=False
        )
        baseline = base_res.predicted_demand
        
        # 2. Simulated forecast with user scenario parameters
        sim_res = forecast_single_item(
            db=db,
            branch_id=request.branch_id,
            menu_item_id=item.id,
            target_date=request.target_date,
            weather_temp=temp,
            rainfall_mm=rainfall,
            weather_condition=request.weather_scenario,
            promotion_active=request.active_promotion,
            holiday_flag=request.is_holiday,
            festival_flag=request.is_festival
        )
        sim_val = sim_res.predicted_demand
        
        # Apply manual demand shift
        if request.demand_shift_percentage != 0.0:
            sim_val *= (1.0 + (request.demand_shift_percentage / 100.0))
            sim_val = max(5.0, round(sim_val, 1))
            
        change_pct = round(((sim_val - baseline) / baseline) * 100.0, 1) if baseline > 0 else 0.0
        recommended_prep = int(round(sim_val * 1.04)) # 4% prudent buffer
        
        # Waste risk calculation:
        # If demand drops significantly or item has short shelf life, risk increases
        if change_pct < -10.0 or item.shelf_life_hours <= 12:
            waste_risk_portions = max(2, int(recommended_prep * 0.12))
            risk_level = "high" if change_pct < -15.0 else "moderate"
        else:
            waste_risk_portions = max(1, int(recommended_prep * 0.05))
            risk_level = "low"
            
        total_baseline += baseline
        total_simulated += sim_val
        total_waste_risk += waste_risk_portions
        
        sim_items.append(SimulatedItemResult(
            menu_item_id=item.id,
            menu_item_name=item.name,
            baseline_demand=round(baseline, 1),
            simulated_demand=round(sim_val, 1),
            demand_change_percentage=change_pct,
            recommended_preparation=recommended_prep,
            predicted_waste_risk_portions=waste_risk_portions,
            risk_level=risk_level
        ))
        
    net_change_pct = round(((total_simulated - total_baseline) / total_baseline) * 100.0, 1) if total_baseline > 0 else 0.0
    
    scenario_desc = (
        f"Scenario: {request.weather_scenario} ({temp}°C, {rainfall}mm rain) | "
        f"Holiday: {request.is_holiday} | Promo: {request.active_promotion} | "
        f"Demand Shift: {request.demand_shift_percentage:+.1f}%"
    )
    
    return WhatIfSimulationResponse(
        branch_id=request.branch_id,
        target_date=request.target_date,
        scenario_description=scenario_desc,
        total_baseline_demand=round(total_baseline, 1),
        total_simulated_demand=round(total_simulated, 1),
        net_demand_change_pct=net_change_pct,
        total_estimated_waste_risk=total_waste_risk,
        key_drivers=key_drivers,
        item_simulations=sim_items
    )
