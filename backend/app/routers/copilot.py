from typing import Optional, Dict, Any, List
from datetime import date
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.config import settings
from backend.app.services.llm_copilot import (
    is_llm_configured,
    generate_executive_kitchen_briefing,
    generate_surplus_repurposing_ideas,
    answer_kitchen_assistant_query
)
from backend.app.services.demand_forecasting import forecast_single_item
from backend.app.services.alert_engine import evaluate_and_generate_alerts
from backend.app.models.entities import MenuItem, Branch

router = APIRouter(prefix="/copilot", tags=["AI Kitchen Copilot (NVIDIA NIM)"])

class SurplusRepurposeRequest(BaseModel):
    menu_item_name: str
    surplus_quantity: int
    shelf_life_hours: Optional[int] = 12

class AskCopilotRequest(BaseModel):
    query: str
    branch_id: Optional[str] = "branch-downtown-01"

@router.get("/status")
def get_copilot_status():
    configured = is_llm_configured()
    return {
        "is_llm_configured": configured,
        "provider": "NVIDIA NIM (Inference Microservices)",
        "model": settings.NVIDIA_MODEL,
        "base_url": settings.NVIDIA_BASE_URL,
        "free_tier_available": True,
        "instructions": (
            "NVIDIA provides free API credits at build.nvidia.com. "
            "Set NVIDIA_API_KEY in your .env file to enable live LLM generation. "
            "When no key is provided, the platform automatically uses high-precision deterministic culinary algorithms."
        )
    }

@router.get("/daily-briefing")
async def get_kitchen_briefing(
    branch_id: str = Query(..., description="Branch identifier"),
    target_date: Optional[date] = Query(None),
    weather_condition: str = Query("Clear"),
    temp_celsius: float = Query(25.0),
    rainfall_mm: float = Query(0.0),
    is_holiday: bool = Query(False),
    db: Session = Depends(get_db)
):
    if target_date is None:
        target_date = date.today()

    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    branch_name = branch.name if branch else "Main Kitchen"

    # Fetch top items
    items = db.query(MenuItem).filter(MenuItem.is_active == True).all()
    forecasts = []
    total_portions = 0.0
    for it in items:
        f = forecast_single_item(
            db=db,
            branch_id=branch_id,
            menu_item_id=it.id,
            target_date=target_date,
            weather_temp=temp_celsius,
            rainfall_mm=rainfall_mm,
            weather_condition=weather_condition,
            holiday_flag=is_holiday
        )
        forecasts.append({"name": it.name, "prep": f.recommended_preparation})
        total_portions += f.predicted_demand

    forecasts.sort(key=lambda x: x["prep"], reverse=True)

    # Fetch alerts
    alerts = evaluate_and_generate_alerts(db, branch_id)
    alert_dicts = [{"title": a.title, "severity": a.severity} for a in alerts]

    return await generate_executive_kitchen_briefing(
        branch_name=branch_name,
        date_str=str(target_date),
        total_portions=total_portions,
        weather_condition=weather_condition,
        temp_celsius=temp_celsius,
        rainfall_mm=rainfall_mm,
        is_holiday=is_holiday,
        top_items=forecasts,
        active_alerts=alert_dicts
    )

@router.post("/surplus-repurpose")
async def repurpose_surplus(payload: SurplusRepurposeRequest):
    return await generate_surplus_repurposing_ideas(
        menu_item_name=payload.menu_item_name,
        surplus_quantity=payload.surplus_quantity,
        shelf_life_hours=payload.shelf_life_hours or 12
    )

@router.post("/ask")
async def ask_copilot(payload: AskCopilotRequest, db: Session = Depends(get_db)):
    context = {
        "branch_id": payload.branch_id,
        "date": str(date.today())
    }
    return await answer_kitchen_assistant_query(payload.query, context)
