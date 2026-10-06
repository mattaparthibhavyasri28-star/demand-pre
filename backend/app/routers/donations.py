from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.donation import (
    SurplusItemDetection,
    FoodSafetyCertificationRequest,
    DonationResponse
)
from backend.app.services.donation_workflow import (
    detect_surplus_candidates,
    register_food_safe_donation,
    list_branch_donations,
    PARTNER_NGOS
)

router = APIRouter(prefix="/donations", tags=["Surplus Food & NGO Donations"])

@router.get("/surplus-candidates", response_model=List[SurplusItemDetection])
def get_surplus_candidates(
    branch_id: str = Query(...),
    db: Session = Depends(get_db)
):
    return detect_surplus_candidates(db, branch_id)

@router.get("/partner-ngos")
def get_partner_ngos():
    return PARTNER_NGOS

@router.post("/certify-and-dispatch", response_model=DonationResponse)
def dispatch_surplus_donation(
    payload: FoodSafetyCertificationRequest,
    db: Session = Depends(get_db)
):
    return register_food_safe_donation(db, payload)

@router.get("", response_model=List[DonationResponse])
def get_branch_donations(
    branch_id: str = Query(...),
    db: Session = Depends(get_db)
):
    return list_branch_donations(db, branch_id)
