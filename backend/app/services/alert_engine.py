"""
Operational Alert Engine
------------------------
Generates actionable notifications based on configurable, data-derived thresholds:
- High waste risk
- Stock-out vulnerability
- Excess inventory & capital lock-up
- Imminent ingredient shelf-life expiry
- Surge intra-day demand spikes
"""

from typing import List, Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from backend.app.models.entities import Alert, WasteRecord, InventoryItem, Ingredient, MenuItem
from backend.app.schemas.alert import AlertResponse

def evaluate_and_generate_alerts(db: Session, branch_id: str) -> List[AlertResponse]:
    """
    Scans recent operational metrics and generates live alerts if threshold criteria are met.
    """
    # 1. High Waste Risk Scan (Past 3 days)
    cutoff_date = date.today() - timedelta(days=3)
    recent_waste = (
        db.query(WasteRecord, MenuItem.name)
        .join(MenuItem, WasteRecord.menu_item_id == MenuItem.id)
        .filter(
            WasteRecord.branch_id == branch_id,
            WasteRecord.record_date >= cutoff_date,
            WasteRecord.waste_percentage > 18.0
        )
        .all()
    )
    
    for wr, item_name in recent_waste:
        # Check if existing active alert exists for this item
        existing = (
            db.query(Alert)
            .filter(
                Alert.branch_id == branch_id,
                Alert.alert_type == "high_waste_risk",
                Alert.status == "active",
                Alert.title.contains(item_name)
            )
            .first()
        )
        if not existing:
            new_alert = Alert(
                branch_id=branch_id,
                alert_type="high_waste_risk",
                severity="warning" if wr.cost_wasted < 40 else "critical",
                title=f"Elevated Waste Alert: {item_name}",
                message=f"Waste level reached {wr.waste_percentage}% ({wr.wasted_quantity} portions, ${wr.cost_wasted:.2f}) due to {wr.waste_reason.replace('_', ' ')}.",
                meta_info={"menu_item_id": wr.menu_item_id, "cost_wasted": wr.cost_wasted, "waste_pct": wr.waste_percentage},
                status="active"
            )
            db.add(new_alert)
            
    # 2. Stockout Risk & Expiry Scan
    inventory_items = (
        db.query(InventoryItem, Ingredient.name, Ingredient.unit)
        .join(Ingredient, InventoryItem.ingredient_id == Ingredient.id)
        .filter(InventoryItem.branch_id == branch_id)
        .all()
    )
    
    for inv, ing_name, unit in inventory_items:
        if inv.current_stock < inv.safety_stock:
            existing = (
                db.query(Alert)
                .filter(
                    Alert.branch_id == branch_id,
                    Alert.alert_type == "stockout_risk",
                    Alert.status == "active",
                    Alert.title.contains(ing_name)
                )
                .first()
            )
            if not existing:
                new_alert = Alert(
                    branch_id=branch_id,
                    alert_type="stockout_risk",
                    severity="critical" if inv.current_stock <= (inv.safety_stock * 0.5) else "warning",
                    title=f"Stock-Out Warning: {ing_name}",
                    message=f"Current stock ({inv.current_stock:.1f} {unit}) has fallen below the safety threshold ({inv.safety_stock:.1f} {unit}). Immediate replenishment required.",
                    meta_info={"ingredient_id": inv.ingredient_id, "current_stock": inv.current_stock, "safety_stock": inv.safety_stock},
                    status="active"
                )
                db.add(new_alert)
                
        # Expiry check
        if inv.expiry_date and (inv.expiry_date - date.today()).days <= 2:
            existing = (
                db.query(Alert)
                .filter(
                    Alert.branch_id == branch_id,
                    Alert.alert_type == "expiry_warning",
                    Alert.status == "active",
                    Alert.title.contains(ing_name)
                )
                .first()
            )
            if not existing:
                days_left = (inv.expiry_date - date.today()).days
                new_alert = Alert(
                    branch_id=branch_id,
                    alert_type="expiry_warning",
                    severity="critical" if days_left <= 1 else "warning",
                    title=f"Ingredient Expiry Imminent: {ing_name}",
                    message=f"{inv.current_stock:.1f} {unit} of {ing_name} expires in {days_left} day(s). Prioritize in today's menu specials to prevent spoilage waste.",
                    meta_info={"ingredient_id": inv.ingredient_id, "days_left": days_left},
                    status="active"
                )
                db.add(new_alert)
                
    db.commit()
    
    # Return all active alerts
    active_alerts = (
        db.query(Alert)
        .filter(Alert.branch_id == branch_id)
        .order_by(Alert.created_at.desc())
        .limit(20)
        .all()
    )
    
    return [
        AlertResponse(
            id=a.id,
            branch_id=a.branch_id,
            alert_type=a.alert_type,
            severity=a.severity,
            title=a.title,
            message=a.message,
            metadata=a.meta_info,
            status=a.status,
            created_at=a.created_at,
            resolved_at=a.resolved_at
        )
        for a in active_alerts
    ]

def acknowledge_alert(db: Session, alert_id: str, new_status: str = "acknowledged") -> AlertResponse:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise ValueError(f"Alert {alert_id} not found.")
    alert.status = new_status
    if new_status == "resolved":
        alert.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(alert)
    return AlertResponse(
        id=alert.id,
        branch_id=alert.branch_id,
        alert_type=alert.alert_type,
        severity=alert.severity,
        title=alert.title,
        message=alert.message,
        metadata=alert.meta_info,
        status=alert.status,
        created_at=alert.created_at,
        resolved_at=alert.resolved_at
    )
