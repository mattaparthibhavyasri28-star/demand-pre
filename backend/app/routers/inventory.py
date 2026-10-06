from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.entities import InventoryItem, Ingredient
from backend.app.schemas.inventory import PurchaseRecommendationResponse
from backend.app.services.inventory_optimizer import calculate_inventory_requirements

router = APIRouter(prefix="/inventory", tags=["Smart Inventory Management"])

@router.get("/recommendations", response_model=PurchaseRecommendationResponse)
def get_inventory_recommendations(
    branch_id: str = Query(..., description="Branch identifier"),
    planning_date: Optional[date] = Query(default=None, description="Planning date"),
    db: Session = Depends(get_db)
):
    if planning_date is None:
        planning_date = date.today()
    return calculate_inventory_requirements(db, branch_id, planning_date)

@router.get("/items")
def get_branch_inventory(
    branch_id: str = Query(...),
    db: Session = Depends(get_db)
):
    items = (
        db.query(InventoryItem, Ingredient)
        .join(Ingredient, InventoryItem.ingredient_id == Ingredient.id)
        .filter(InventoryItem.branch_id == branch_id)
        .all()
    )
    return [
        {
            "id": inv.id,
            "ingredient_id": ing.id,
            "name": ing.name,
            "category": ing.category,
            "current_stock": inv.current_stock,
            "safety_stock": inv.safety_stock,
            "reorder_point": inv.reorder_point,
            "unit": inv.unit,
            "unit_cost": ing.unit_cost,
            "expiry_date": inv.expiry_date.isoformat() if inv.expiry_date else None,
            "last_restocked_at": inv.last_restocked_at.isoformat() if inv.last_restocked_at else None
        }
        for inv, ing in items
    ]
