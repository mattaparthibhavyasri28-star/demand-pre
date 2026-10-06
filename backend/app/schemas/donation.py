from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class SurplusItemDetection(BaseModel):
    menu_item_id: str
    menu_item_name: str
    surplus_quantity: int
    unit: str
    safe_to_donate: bool
    recommended_discount_portion: int
    recommended_donation_portion: int
    estimated_shelf_life_remaining_hours: int

class FoodSafetyCertificationRequest(BaseModel):
    branch_id: str
    menu_item_id: str
    surplus_quantity: int = Field(gt=0)
    certified_by: str
    temperature_verified_celsius: float
    visual_inspection_passed: bool
    packaging_intact: bool
    recipient_ngo: str
    contact_phone: Optional[str] = None
    notes: Optional[str] = None

class DonationResponse(BaseModel):
    id: str
    branch_id: str
    menu_item_id: str
    menu_item_name: str
    surplus_quantity: int
    unit: str
    food_safe_certified: bool
    certified_by: Optional[str]
    recipient_ngo: Optional[str]
    pickup_status: str # pending, scheduled, picked_up, delivered
    impact_meals_saved: int
    carbon_avoided_kg: float
    created_at: datetime
    disclaimer: str = "Food safety acceptance requires manual authorized verification. The system assists logistics and impact tracking."
