from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.sustainability import SustainabilitySummary
from backend.app.services.sustainability_calc import calculate_sustainability_metrics

router = APIRouter(prefix="/sustainability", tags=["Sustainability & Environmental Impact"])

@router.get("/summary", response_model=SustainabilitySummary)
def get_sustainability_summary(
    branch_id: str = Query(...),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    return calculate_sustainability_metrics(db, branch_id, days)
