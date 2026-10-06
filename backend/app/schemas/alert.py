from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel

class AlertResponse(BaseModel):
    id: str
    branch_id: str
    alert_type: str # high_waste_risk, stockout_risk, excess_inventory, expiry_warning, surge_demand
    severity: str # info, warning, critical
    title: str
    message: str
    metadata: Optional[Dict[str, Any]] = None
    status: str # active, acknowledged, resolved
    created_at: datetime
    resolved_at: Optional[datetime] = None

class AlertAcknowledgeRequest(BaseModel):
    alert_id: str
    status: str # acknowledged, resolved
