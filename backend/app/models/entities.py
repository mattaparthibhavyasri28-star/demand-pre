import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Date, DateTime,
    ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from backend.app.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    contact_email = Column(String(255), nullable=True)
    currency = Column(String(10), default="USD")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    branches = relationship("Branch", back_populates="restaurant", cascade="all, delete-orphan")
    menu_items = relationship("MenuItem", back_populates="restaurant", cascade="all, delete-orphan")
    ingredients = relationship("Ingredient", back_populates="restaurant", cascade="all, delete-orphan")

class Branch(Base):
    __tablename__ = "branches"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    restaurant_id = Column(String(36), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    timezone = Column(String(50), default="UTC")
    opening_time = Column(String(10), default="09:00:00")
    closing_time = Column(String(10), default="23:00:00")
    created_at = Column(DateTime, default=datetime.utcnow)

    restaurant = relationship("Restaurant", back_populates="branches")
    sales = relationship("SalesRecord", back_populates="branch", cascade="all, delete-orphan")
    waste_records = relationship("WasteRecord", back_populates="branch", cascade="all, delete-orphan")
    inventory = relationship("InventoryItem", back_populates="branch", cascade="all, delete-orphan")
    predictions = relationship("DemandPrediction", back_populates="branch", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="branch", cascade="all, delete-orphan")
    donations = relationship("SurplusDonation", back_populates="branch", cascade="all, delete-orphan")

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    restaurant_id = Column(String(36), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False) # Main, Appetizer, Dessert, Beverage
    selling_price = Column(Float, nullable=False)
    preparation_cost = Column(Float, nullable=False)
    shelf_life_hours = Column(Integer, default=24)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    restaurant = relationship("Restaurant", back_populates="menu_items")
    recipes = relationship("RecipeItem", back_populates="menu_item", cascade="all, delete-orphan")
    sales = relationship("SalesRecord", back_populates="menu_item")
    waste_records = relationship("WasteRecord", back_populates="menu_item")
    predictions = relationship("DemandPrediction", back_populates="menu_item")

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    restaurant_id = Column(String(36), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False) # Dairy, Meat, Produce, Dry Goods
    unit = Column(String(50), nullable=False) # kg, g, liters, count
    unit_cost = Column(Float, nullable=False)
    shelf_life_days = Column(Integer, default=7)
    created_at = Column(DateTime, default=datetime.utcnow)

    restaurant = relationship("Restaurant", back_populates="ingredients")
    recipe_usages = relationship("RecipeItem", back_populates="ingredient")
    inventory_items = relationship("InventoryItem", back_populates="ingredient")

class RecipeItem(Base):
    __tablename__ = "recipe_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    menu_item_id = Column(String(36), ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=False)
    ingredient_id = Column(String(36), ForeignKey("ingredients.id", ondelete="RESTRICT"), nullable=False)
    quantity_required = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)

    menu_item = relationship("MenuItem", back_populates="recipes")
    ingredient = relationship("Ingredient", back_populates="recipe_usages")

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    branch_id = Column(String(36), ForeignKey("branches.id", ondelete="CASCADE"), nullable=False)
    ingredient_id = Column(String(36), ForeignKey("ingredients.id", ondelete="RESTRICT"), nullable=False)
    current_stock = Column(Float, default=0.0)
    safety_stock = Column(Float, default=10.0)
    reorder_point = Column(Float, default=20.0)
    unit = Column(String(50), nullable=False)
    expiry_date = Column(Date, nullable=True)
    last_restocked_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    branch = relationship("Branch", back_populates="inventory")
    ingredient = relationship("Ingredient", back_populates="inventory_items")

class SalesRecord(Base):
    __tablename__ = "sales_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    branch_id = Column(String(36), ForeignKey("branches.id", ondelete="CASCADE"), nullable=False)
    menu_item_id = Column(String(36), ForeignKey("menu_items.id", ondelete="RESTRICT"), nullable=False)
    sale_date = Column(Date, nullable=False)
    sale_hour = Column(Integer, nullable=True)
    quantity_sold = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    promotion_active = Column(Boolean, default=False)
    holiday_flag = Column(Boolean, default=False)
    weather_temp = Column(Float, nullable=True)
    rainfall_mm = Column(Float, default=0.0)
    weather_condition = Column(String(100), default="Clear")
    source = Column(String(50), default="pos_batch") # pos_batch, pos_realtime, manual, synthetic
    created_at = Column(DateTime, default=datetime.utcnow)

    branch = relationship("Branch", back_populates="sales")
    menu_item = relationship("MenuItem", back_populates="sales")

class WasteRecord(Base):
    __tablename__ = "waste_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    branch_id = Column(String(36), ForeignKey("branches.id", ondelete="CASCADE"), nullable=False)
    menu_item_id = Column(String(36), ForeignKey("menu_items.id", ondelete="RESTRICT"), nullable=False)
    record_date = Column(Date, nullable=False)
    prepared_quantity = Column(Integer, nullable=False)
    sold_quantity = Column(Integer, nullable=False)
    remaining_quantity = Column(Integer, nullable=False)
    wasted_quantity = Column(Integer, nullable=False)
    waste_percentage = Column(Float, nullable=False)
    waste_reason = Column(String(100), nullable=False) # over_production, expired_shelf_life, preparation_error, customer_leftover, spoilage
    cost_wasted = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    corrective_action_recommended = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    branch = relationship("Branch", back_populates="waste_records")
    menu_item = relationship("MenuItem", back_populates="waste_records")

class DemandPrediction(Base):
    __tablename__ = "demand_predictions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    branch_id = Column(String(36), ForeignKey("branches.id", ondelete="CASCADE"), nullable=False)
    menu_item_id = Column(String(36), ForeignKey("menu_items.id", ondelete="RESTRICT"), nullable=False)
    target_date = Column(Date, nullable=False)
    predicted_demand = Column(Float, nullable=False)
    confidence_lower = Column(Float, nullable=False)
    confidence_upper = Column(Float, nullable=False)
    recommended_preparation = Column(Integer, nullable=False)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    feature_contributions = Column(JSON, nullable=True)
    actual_demand = Column(Integer, nullable=True)
    absolute_error = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    branch = relationship("Branch", back_populates="predictions")
    menu_item = relationship("MenuItem", back_populates="predictions")

class ModelEvaluation(Base):
    __tablename__ = "model_evaluations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    evaluation_date = Column(DateTime, default=datetime.utcnow)
    dataset_period = Column(String(100), nullable=True)
    sample_count = Column(Integer, nullable=False)
    mae = Column(Float, nullable=False)
    rmse = Column(Float, nullable=False)
    mape = Column(Float, nullable=True)
    r2_score = Column(Float, nullable=False)
    is_active_model = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    branch_id = Column(String(36), ForeignKey("branches.id", ondelete="CASCADE"), nullable=False)
    alert_type = Column(String(100), nullable=False) # high_waste_risk, stockout_risk, excess_inventory, expiry_warning, surge_demand
    severity = Column(String(20), nullable=False) # info, warning, critical
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    meta_info = Column(JSON, nullable=True)
    status = Column(String(50), default="active") # active, acknowledged, resolved
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    branch = relationship("Branch", back_populates="alerts")

class SurplusDonation(Base):
    __tablename__ = "surplus_donations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    branch_id = Column(String(36), ForeignKey("branches.id", ondelete="CASCADE"), nullable=False)
    menu_item_id = Column(String(36), ForeignKey("menu_items.id", ondelete="RESTRICT"), nullable=False)
    surplus_quantity = Column(Integer, nullable=False)
    unit = Column(String(50), default="portions")
    food_safe_certified = Column(Boolean, default=False)
    certified_by = Column(String(255), nullable=True)
    certification_timestamp = Column(DateTime, nullable=True)
    recipient_ngo = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    pickup_status = Column(String(50), default="pending") # pending, scheduled, picked_up, delivered, rejected
    impact_meals_saved = Column(Integer, default=0)
    carbon_avoided_kg = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    branch = relationship("Branch", back_populates="donations")
