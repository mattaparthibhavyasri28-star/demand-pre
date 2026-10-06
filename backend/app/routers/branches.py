from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.entities import Branch, Restaurant, MenuItem

router = APIRouter(prefix="/branches", tags=["Restaurants & Branches"])

@router.get("")
def list_branches(db: Session = Depends(get_db)):
    branches = db.query(Branch, Restaurant.name.label("restaurant_name")).join(Restaurant).all()
    return [
        {
            "id": b.Branch.id,
            "restaurant_id": b.Branch.restaurant_id,
            "restaurant_name": b.restaurant_name,
            "name": b.Branch.name,
            "city": b.Branch.city,
            "address": b.Branch.address,
            "timezone": b.Branch.timezone,
            "opening_time": b.Branch.opening_time,
            "closing_time": b.Branch.closing_time
        }
        for b in branches
    ]

@router.get("/{branch_id}/menu")
def get_branch_menu(branch_id: str, db: Session = Depends(get_db)):
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found.")
        
    items = db.query(MenuItem).filter(MenuItem.restaurant_id == branch.restaurant_id, MenuItem.is_active == True).all()
    return [
        {
            "id": m.id,
            "name": m.name,
            "category": m.category,
            "selling_price": m.selling_price,
            "preparation_cost": m.preparation_cost,
            "shelf_life_hours": m.shelf_life_hours
        }
        for m in items
    ]
