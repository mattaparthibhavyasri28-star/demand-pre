from typing import List
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.alert import AlertResponse, AlertAcknowledgeRequest
from backend.app.services.alert_engine import evaluate_and_generate_alerts, acknowledge_alert

router = APIRouter(prefix="/alerts", tags=["Operational Alerts"])

@router.get("", response_model=List[AlertResponse])
def get_alerts(
    branch_id: str = Query(..., description="Branch identifier"),
    db: Session = Depends(get_db)
):
    return evaluate_and_generate_alerts(db, branch_id)

@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
def update_alert_status(
    alert_id: str = Path(..., description="Alert ID"),
    payload: AlertAcknowledgeRequest = None,
    db: Session = Depends(get_db)
):
    status = payload.status if payload else "acknowledged"
    return acknowledge_alert(db, alert_id, status)
