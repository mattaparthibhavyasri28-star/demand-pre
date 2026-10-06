from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.simulation import (
    WhatIfSimulationRequest,
    WhatIfSimulationResponse
)
from backend.app.services.what_if_simulator import run_what_if_simulation

router = APIRouter(prefix="/simulation", tags=["What-If Scenario Simulation"])

@router.post("/what-if", response_model=WhatIfSimulationResponse)
def simulate_scenario(request: WhatIfSimulationRequest, db: Session = Depends(get_db)):
    return run_what_if_simulation(db, request)
