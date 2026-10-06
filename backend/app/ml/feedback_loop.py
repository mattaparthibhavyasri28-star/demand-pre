"""
Closed ML Feedback Loop & Continuous Evaluation Engine
------------------------------------------------------
Compares predictions against actual observed sales, monitors error drift,
and computes corrective feedback multipliers to prevent repetitive over-preparation.
"""

from typing import Dict, Any, List, Optional
from datetime import date
import numpy as np
from sqlalchemy.orm import Session
from backend.app.models.entities import DemandPrediction, SalesRecord, WasteRecord

def evaluate_recent_prediction_bias(
    db: Session,
    branch_id: str,
    menu_item_id: str,
    lookback_days: int = 7
) -> Dict[str, Any]:
    """
    Computes recent prediction accuracy, mean error, and closed-loop feedback multiplier.
    If the system consistently over-predicted, the feedback multiplier reduces tomorrow's prep.
    """
    # Fetch recent predictions that have actual sales recorded
    recent_preds = (
        db.query(DemandPrediction)
        .filter(
            DemandPrediction.branch_id == branch_id,
            DemandPrediction.menu_item_id == menu_item_id,
            DemandPrediction.actual_demand.isnot(None)
        )
        .order_by(DemandPrediction.target_date.desc())
        .limit(lookback_days)
        .all()
    )
    
    if not recent_preds or len(recent_preds) < 3:
        # Insufficient paired history, return neutral feedback
        return {
            "has_sufficient_history": False,
            "sample_size": len(recent_preds),
            "mean_signed_error": 0.0,
            "feedback_multiplier": 1.0,
            "status": "normal",
            "message": "Historical paired records building. Using baseline model weights."
        }
        
    signed_errors = [p.predicted_demand - p.actual_demand for p in recent_preds]
    mean_error = float(np.mean(signed_errors))
    abs_errors = [abs(e) for e in signed_errors]
    mae = float(np.mean(abs_errors))
    
    # If mean_error > 5.0, model has systematic positive bias (over-predicting demand)
    # -> Which directly leads to excess kitchen preparation and waste!
    if mean_error > 6.0:
        # Dampen preparation by ~5% to 10%
        feedback_multiplier = 0.92
        status = "over_predicting"
        msg = f"Systematic over-prediction detected (avg +{mean_error:.1f} portions). Feedback loop applied 8% downward preparation guardrail."
    elif mean_error < -6.0:
        feedback_multiplier = 1.06
        status = "under_predicting"
        msg = f"Consistent under-prediction observed (avg {mean_error:.1f} portions). Slight preparation buffer (+6%) recommended to avoid stock-outs."
    else:
        feedback_multiplier = 1.0
        status = "well_calibrated"
        msg = f"Predictions well-calibrated (MAE {mae:.1f} portions, bias {mean_error:.1f})."
        
    return {
        "has_sufficient_history": True,
        "sample_size": len(recent_preds),
        "mean_signed_error": round(mean_error, 2),
        "mae": round(mae, 2),
        "feedback_multiplier": feedback_multiplier,
        "status": status,
        "message": msg
    }
