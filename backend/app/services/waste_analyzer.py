"""
Food Waste Tracking & Root Cause Analysis Service
-------------------------------------------------
Logs granular kitchen waste records, analyzes causal patterns across items,
and generates actionable corrective feedback to reduce recurring waste.
"""

from typing import List, Dict, Any, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.models.entities import WasteRecord, MenuItem
from backend.app.schemas.waste import (
    WasteLogCreate,
    WasteRecordResponse,
    WasteCauseBreakdown,
    ActionableRecommendation,
    WasteAnalyticsResponse
)

REASON_DISPLAY_NAMES = {
    "over_production": "Over-Production",
    "expired_shelf_life": "Expired Shelf Life",
    "preparation_error": "Kitchen Preparation Error",
    "customer_leftover": "Customer Plate Leftovers",
    "spoilage": "Storage Spoilage",
    "none": "No Waste"
}

def log_waste_entry(db: Session, entry: WasteLogCreate) -> WasteRecordResponse:
    item = db.query(MenuItem).filter(MenuItem.id == entry.menu_item_id).first()
    prep_cost = item.preparation_cost if item else 4.0
    item_name = item.name if item else "Menu Item"
    
    waste_pct = round((entry.wasted_quantity / entry.prepared_quantity) * 100, 2) if entry.prepared_quantity > 0 else 0.0
    cost_wasted = round(entry.wasted_quantity * prep_cost, 2)
    
    # Actionable corrective recommendation attached to this specific entry
    corrective_action = None
    if entry.waste_reason == "over_production" and entry.wasted_quantity > 8:
        corrective_action = f"Trim tomorrow's pre-cook batch by {int(entry.wasted_quantity * 0.7)} portions. Stage fresh batches in near-real-time."
    elif entry.waste_reason == "expired_shelf_life":
        corrective_action = "Rotate walk-in refrigeration using strict FIFO tagging. Verify hot-holding temperature logs."
    elif entry.waste_reason == "preparation_error":
        corrective_action = "Review standardized recipe proportions and chef station prep instructions."
        
    record = WasteRecord(
        branch_id=entry.branch_id,
        menu_item_id=entry.menu_item_id,
        record_date=entry.record_date,
        prepared_quantity=entry.prepared_quantity,
        sold_quantity=entry.sold_quantity,
        remaining_quantity=entry.remaining_quantity,
        wasted_quantity=entry.wasted_quantity,
        waste_percentage=waste_pct,
        waste_reason=entry.waste_reason,
        cost_wasted=cost_wasted,
        notes=entry.notes,
        corrective_action_recommended=corrective_action
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return WasteRecordResponse(
        id=record.id,
        branch_id=record.branch_id,
        menu_item_id=record.menu_item_id,
        menu_item_name=item_name,
        record_date=record.record_date,
        prepared_quantity=record.prepared_quantity,
        sold_quantity=record.sold_quantity,
        remaining_quantity=record.remaining_quantity,
        wasted_quantity=record.wasted_quantity,
        waste_percentage=record.waste_percentage,
        waste_reason=record.waste_reason,
        cost_wasted=record.cost_wasted,
        notes=record.notes,
        corrective_action_recommended=record.corrective_action_recommended,
        created_at=record.created_at
    )

def get_waste_analytics(
    db: Session,
    branch_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> WasteAnalyticsResponse:
    if end_date is None:
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=30)
        
    records = (
        db.query(WasteRecord, MenuItem.name)
        .join(MenuItem, WasteRecord.menu_item_id == MenuItem.id)
        .filter(
            WasteRecord.branch_id == branch_id,
            WasteRecord.record_date >= start_date,
            WasteRecord.record_date <= end_date
        )
        .order_by(WasteRecord.record_date.desc())
        .all()
    )
    
    total_prep = 0
    total_sold = 0
    total_wasted = 0
    total_cost_wasted = 0.0
    
    reason_counts: Dict[str, int] = {}
    reason_costs: Dict[str, float] = {}
    item_waste_aggregates: Dict[str, Dict[str, Any]] = {}
    recent_responses: List[WasteRecordResponse] = []
    
    for r, item_name in records:
        total_prep += r.prepared_quantity
        total_sold += r.sold_quantity
        total_wasted += r.wasted_quantity
        total_cost_wasted += r.cost_wasted
        
        reason = r.waste_reason
        reason_counts[reason] = reason_counts.get(reason, 0) + r.wasted_quantity
        reason_costs[reason] = reason_costs.get(reason, 0.0) + r.cost_wasted
        
        # Track by item for root cause detection
        if r.menu_item_id not in item_waste_aggregates:
            item_waste_aggregates[r.menu_item_id] = {
                "name": item_name,
                "over_production_qty": 0,
                "total_wasted": 0,
                "cost_wasted": 0.0
            }
        item_waste_aggregates[r.menu_item_id]["total_wasted"] += r.wasted_quantity
        item_waste_aggregates[r.menu_item_id]["cost_wasted"] += r.cost_wasted
        if r.waste_reason == "over_production":
            item_waste_aggregates[r.menu_item_id]["over_production_qty"] += r.wasted_quantity
            
        recent_responses.append(WasteRecordResponse(
            id=r.id,
            branch_id=r.branch_id,
            menu_item_id=r.menu_item_id,
            menu_item_name=item_name,
            record_date=r.record_date,
            prepared_quantity=r.prepared_quantity,
            sold_quantity=r.sold_quantity,
            remaining_quantity=r.remaining_quantity,
            wasted_quantity=r.wasted_quantity,
            waste_percentage=r.waste_percentage,
            waste_reason=r.waste_reason,
            cost_wasted=r.cost_wasted,
            notes=r.notes,
            corrective_action_recommended=r.corrective_action_recommended,
            created_at=r.created_at
        ))
        
    overall_waste_pct = round((total_wasted / total_prep) * 100, 2) if total_prep > 0 else 0.0
    
    # Compile Cause Breakdown
    cause_breakdown: List[WasteCauseBreakdown] = []
    for reason, qty in reason_counts.items():
        if reason == "none":
            continue
        cost = round(reason_costs.get(reason, 0.0), 2)
        pct_of_waste = round((qty / total_wasted) * 100, 1) if total_wasted > 0 else 0.0
        cause_breakdown.append(WasteCauseBreakdown(
            reason=reason,
            display_name=REASON_DISPLAY_NAMES.get(reason, reason.replace("_", " ").title()),
            quantity=qty,
            cost=cost,
            percentage_of_total_waste=pct_of_waste
        ))
        
    cause_breakdown.sort(key=lambda x: x.quantity, reverse=True)
    
    # Generate actionable recommendations from detected patterns
    recommendations: List[ActionableRecommendation] = []
    for item_id, stats in item_waste_aggregates.items():
        if stats["over_production_qty"] > 20:
            rec_cut = int(stats["over_production_qty"] / 10)
            rec_savings = round(stats["cost_wasted"] * 0.35, 2)
            recommendations.append(ActionableRecommendation(
                menu_item_id=item_id,
                menu_item_name=stats["name"],
                issue_detected=f"Repeated over-production ({stats['over_production_qty']} portions wasted across reporting period).",
                recommended_action=f"Reduce daily initial prep batch by ~{rec_cut} portions. Enable near-real-time intra-day tracking.",
                expected_savings_portions=rec_cut * 7,
                expected_cost_reduction=rec_savings
            ))
            
    return WasteAnalyticsResponse(
        branch_id=branch_id,
        start_date=start_date,
        end_date=end_date,
        total_prepared=total_prep,
        total_sold=total_sold,
        total_wasted=total_wasted,
        overall_waste_percentage=overall_waste_pct,
        total_cost_wasted=round(total_cost_wasted, 2),
        cause_breakdown=cause_breakdown,
        actionable_recommendations=recommendations,
        recent_logs=recent_responses[:50]
    )
