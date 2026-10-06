"""
Surplus Food & NGO Donation Workflow Engine
-------------------------------------------
Coordinates safe surplus redistribution to local partner charities and NGOs.

Crucial Food Safety Principle:
The system identifies potential surplus and streamlines logistics, but does NOT
independently certify microbiological or thermal food safety. Authorized kitchen
and partner personnel must certify visual, temperature, and packaging compliance.
"""

from typing import List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from backend.app.models.entities import SurplusDonation, WasteRecord, MenuItem
from backend.app.schemas.donation import (
    SurplusItemDetection,
    FoodSafetyCertificationRequest,
    DonationResponse
)

PARTNER_NGOS = [
    {"name": "City Harvest Community Food Bank", "phone": "+1-555-019-2831"},
    {"name": "Feeding Families Shelter Network", "phone": "+1-555-014-9822"},
    {"name": "No Waste Kitchen Coalition", "phone": "+1-555-018-7740"}
]

def detect_surplus_candidates(db: Session, branch_id: str) -> List[SurplusItemDetection]:
    """
    Identifies clean remaining prepared items from recent service that can be
    safely diverted to donations or evening discount specials before disposal.
    """
    today = date.today()
    recent_surplus = (
        db.query(WasteRecord, MenuItem)
        .join(MenuItem, WasteRecord.menu_item_id == MenuItem.id)
        .filter(
            WasteRecord.branch_id == branch_id,
            WasteRecord.record_date >= today - timedelta(days=1),
            WasteRecord.remaining_quantity > 0,
            WasteRecord.waste_reason.in_(["over_production", "none"])
        )
        .all()
    )
    
    candidates: List[SurplusItemDetection] = []
    seen_items = set()
    
    for wr, item in recent_surplus:
        if wr.menu_item_id in seen_items:
            continue
        seen_items.add(wr.menu_item_id)
        
        remaining = wr.remaining_quantity
        safe = item.shelf_life_hours >= 12
        disc_part = int(remaining * 0.4)
        donate_part = remaining - disc_part
        
        candidates.append(SurplusItemDetection(
            menu_item_id=item.id,
            menu_item_name=item.name,
            surplus_quantity=remaining,
            unit="portions",
            safe_to_donate=safe,
            recommended_discount_portion=disc_part,
            recommended_donation_portion=donate_part,
            estimated_shelf_life_remaining_hours=item.shelf_life_hours
        ))
        
    return candidates

def register_food_safe_donation(
    db: Session,
    cert_request: FoodSafetyCertificationRequest
) -> DonationResponse:
    """
    Records a verified surplus donation once human staff has validated thermal and visual safety.
    """
    if not cert_request.visual_inspection_passed or not cert_request.packaging_intact:
        raise ValueError("Cannot dispatch donation: Visual inspection or packaging integrity failed.")
        
    item = db.query(MenuItem).filter(MenuItem.id == cert_request.menu_item_id).first()
    item_name = item.name if item else "Menu Item"
    
    # Impact metrics:
    # 1 portion = 1 meal saved
    # Approx 2.5 kg CO2e avoided per portion (~400g prepared food)
    meals_saved = cert_request.surplus_quantity
    carbon_avoided = round(cert_request.surplus_quantity * 0.40 * 2.5, 2)
    
    donation = SurplusDonation(
        branch_id=cert_request.branch_id,
        menu_item_id=cert_request.menu_item_id,
        surplus_quantity=cert_request.surplus_quantity,
        unit="portions",
        food_safe_certified=True,
        certified_by=cert_request.certified_by,
        certification_timestamp=datetime.utcnow(),
        recipient_ngo=cert_request.recipient_ngo,
        contact_phone=cert_request.contact_phone,
        pickup_status="scheduled",
        impact_meals_saved=meals_saved,
        carbon_avoided_kg=carbon_avoided
    )
    db.add(donation)
    db.commit()
    db.refresh(donation)
    
    return DonationResponse(
        id=donation.id,
        branch_id=donation.branch_id,
        menu_item_id=donation.menu_item_id,
        menu_item_name=item_name,
        surplus_quantity=donation.surplus_quantity,
        unit=donation.unit,
        food_safe_certified=donation.food_safe_certified,
        certified_by=donation.certified_by,
        recipient_ngo=donation.recipient_ngo,
        pickup_status=donation.pickup_status,
        impact_meals_saved=donation.impact_meals_saved,
        carbon_avoided_kg=donation.carbon_avoided_kg,
        created_at=donation.created_at
    )

def list_branch_donations(db: Session, branch_id: str) -> List[DonationResponse]:
    donations = (
        db.query(SurplusDonation, MenuItem.name)
        .join(MenuItem, SurplusDonation.menu_item_id == MenuItem.id)
        .filter(SurplusDonation.branch_id == branch_id)
        .order_by(SurplusDonation.created_at.desc())
        .all()
    )
    return [
        DonationResponse(
            id=d.id,
            branch_id=d.branch_id,
            menu_item_id=d.menu_item_id,
            menu_item_name=item_name,
            surplus_quantity=d.surplus_quantity,
            unit=d.unit,
            food_safe_certified=d.food_safe_certified,
            certified_by=d.certified_by,
            recipient_ngo=d.recipient_ngo,
            pickup_status=d.pickup_status,
            impact_meals_saved=d.impact_meals_saved,
            carbon_avoided_kg=d.carbon_avoided_kg,
            created_at=d.created_at
        )
        for d, item_name in donations
    ]
