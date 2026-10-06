from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.waste import (
    WasteLogCreate,
    WasteRecordResponse,
    WasteAnalyticsResponse
)
from backend.app.services.waste_analyzer import log_waste_entry, get_waste_analytics

router = APIRouter(prefix="/waste", tags=["Food Waste Tracking & Root Cause Analysis"])

@router.post("/log", response_model=WasteRecordResponse)
def create_waste_log(entry: WasteLogCreate, db: Session = Depends(get_db)):
    return log_waste_entry(db, entry)

@router.get("/analytics", response_model=WasteAnalyticsResponse)
def get_waste_dashboard_analytics(
    branch_id: str = Query(..., description="Branch identifier"),
    start_date: Optional[date] = Query(None, description="Start date for reporting"),
    end_date: Optional[date] = Query(None, description="End date for reporting"),
    db: Session = Depends(get_db)
):
    return get_waste_analytics(db, branch_id, start_date, end_date)
