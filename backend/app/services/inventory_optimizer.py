"""
Smart Inventory Optimizer & Purchase Recommendation Engine
----------------------------------------------------------
Translates forecasted portion demands into exact raw ingredient requirements
using recipe bills of materials (BOM), calculates mathematically grounded
safety stock thresholds, and recommends optimal procurement orders.

Formula:
  Recommended Purchase = max(0, Predicted Demand + Safety Stock - Current Stock)
  Safety Stock = Z * sqrt(Lead Time Days) * Std Dev(Daily Demand)
  where Z = 1.65 for a 95% service level.
"""

import math
from typing import List, Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from backend.app.models.entities import (
    MenuItem,
    Ingredient,
    RecipeItem,
    InventoryItem
)
from backend.app.schemas.inventory import (
    IngredientRequirement,
    PurchaseRecommendationResponse
)
from backend.app.services.demand_forecasting import forecast_single_item

SERVICE_LEVEL_Z = 1.65 # 95% service level
DEFAULT_LEAD_TIME_DAYS = 2.0

def calculate_inventory_requirements(
    db: Session,
    branch_id: str,
    planning_date: date
) -> PurchaseRecommendationResponse:
    # 1. Fetch all active menu items for branch restaurant
    menu_items = db.query(MenuItem).filter(MenuItem.is_active == True).all()
    
    # 2. Forecast demand for each item
    item_demands: Dict[str, float] = {}
    for item in menu_items:
        pred_res = forecast_single_item(db, branch_id, item.id, planning_date)
        item_demands[item.id] = pred_res.predicted_demand
        
    # 3. Aggregate ingredient consumption across all recipes
    ingredient_consumption: Dict[str, float] = {} # ingredient_id -> total qty required
    
    recipe_items = db.query(RecipeItem).all()
    for recipe in recipe_items:
        if recipe.menu_item_id in item_demands:
            portions = item_demands[recipe.menu_item_id]
            ing_req = portions * recipe.quantity_required
            ingredient_consumption[recipe.ingredient_id] = (
                ingredient_consumption.get(recipe.ingredient_id, 0.0) + ing_req
            )
            
    # 4. Fetch current inventory and ingredients
    inventory_records = (
        db.query(InventoryItem)
        .filter(InventoryItem.branch_id == branch_id)
        .all()
    )
    inv_map = {inv.ingredient_id: inv for inv in inventory_records}
    all_ingredients = db.query(Ingredient).all()
    
    recommendations: List[IngredientRequirement] = []
    total_cost = 0.0
    items_to_reorder = 0
    
    for ing in all_ingredients:
        predicted_usage = round(ingredient_consumption.get(ing.id, 0.0), 2)
        inv = inv_map.get(ing.id)
        
        current_stock = inv.current_stock if inv else 15.0
        
        # Calculate documented Safety Stock
        # Std dev is approximated as ~20% of mean daily consumption
        std_dev = max(1.5, predicted_usage * 0.20)
        safety_stock = round(SERVICE_LEVEL_Z * math.sqrt(DEFAULT_LEAD_TIME_DAYS) * std_dev, 2)
        reorder_point = round((predicted_usage * DEFAULT_LEAD_TIME_DAYS) + safety_stock, 2)
        
        # Recommended purchase: max(0, Predicted + Safety - Current)
        gross_need = predicted_usage + safety_stock
        net_deficit = round(gross_need - current_stock, 2)
        recommended_purchase = max(0.0, net_deficit)
        
        est_cost = round(recommended_purchase * ing.unit_cost, 2)
        
        # Urgency classification
        if current_stock < safety_stock and recommended_purchase > 0:
            urgency = "critical_stockout"
            items_to_reorder += 1
        elif current_stock <= reorder_point and recommended_purchase > 0:
            urgency = "reorder_needed"
            items_to_reorder += 1
        else:
            urgency = "normal"
            
        total_cost += est_cost
        
        recommendations.append(IngredientRequirement(
            ingredient_id=ing.id,
            ingredient_name=ing.name,
            category=ing.category,
            unit=ing.unit,
            unit_cost=ing.unit_cost,
            current_stock=round(current_stock, 2),
            predicted_demand_consumption=predicted_usage,
            safety_stock=safety_stock,
            reorder_point=reorder_point,
            net_deficit=net_deficit,
            recommended_purchase=recommended_purchase,
            estimated_purchase_cost=est_cost,
            urgency=urgency
        ))
        
    methodology = (
        f"Inventory recommendations derived using: "
        f"Purchase = max(0, Predicted Demand + Safety Stock - Current Stock). "
        f"Safety Stock calculated with Z={SERVICE_LEVEL_Z} (95% service level) over {DEFAULT_LEAD_TIME_DAYS} days supplier lead time."
    )
    
    return PurchaseRecommendationResponse(
        branch_id=branch_id,
        planning_date=planning_date,
        total_estimated_purchase_cost=round(total_cost, 2),
        items_requiring_reorder=items_to_reorder,
        recommendations=recommendations,
        methodology_notes=methodology
    )
