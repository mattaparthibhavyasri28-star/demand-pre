"""
Database Seeding & Catalog Initialization
-----------------------------------------
Populates database with default restaurant, branch, catalog items, recipes,
inventory stocks, and initial 90 days of operational sales and waste logs.
"""

from datetime import date, timedelta
from sqlalchemy.orm import Session
from backend.app.models.entities import (
    Restaurant,
    Branch,
    MenuItem,
    Ingredient,
    RecipeItem,
    InventoryItem,
    SalesRecord,
    WasteRecord,
    Alert
)
from backend.app.ml.dataset_generator import (
    MENU_ITEMS_CATALOG,
    INGREDIENTS_CATALOG,
    RECIPE_MAPPINGS,
    generate_synthetic_data
)

DEFAULT_RESTAURANT_ID = "rest-green-plate-01"
DEFAULT_BRANCH_ID = "branch-downtown-01"

def seed_database_if_empty(db: Session):
    existing_rest = db.query(Restaurant).filter(Restaurant.id == DEFAULT_RESTAURANT_ID).first()
    if existing_rest:
        return # Already seeded
        
    print("Seeding database with default catalog, recipes, and operational records...")
    
    # 1. Restaurant & Branch
    restaurant = Restaurant(
        id=DEFAULT_RESTAURANT_ID,
        name="The Green Plate Bistro",
        description="Sustainable farm-to-table urban dining with zero-waste culinary practices.",
        contact_email="manager@greenplatebistro.com",
        currency="USD"
    )
    db.add(restaurant)
    
    branch = Branch(
        id=DEFAULT_BRANCH_ID,
        restaurant_id=DEFAULT_RESTAURANT_ID,
        name="Downtown Flagship Branch",
        address="100 Innovation Avenue",
        city="Metropolis",
        timezone="America/New_York",
        opening_time="10:00:00",
        closing_time="22:30:00"
    )
    db.add(branch)
    db.commit()
    
    # 2. Menu Items
    for item in MENU_ITEMS_CATALOG:
        m_item = MenuItem(
            id=item["id"],
            restaurant_id=DEFAULT_RESTAURANT_ID,
            name=item["name"],
            category=item["category"],
            selling_price=item["price"],
            preparation_cost=item["prep_cost"],
            shelf_life_hours=item["shelf_life_hours"],
            is_active=True
        )
        db.add(m_item)
    db.commit()
    
    # 3. Ingredients
    for ing in INGREDIENTS_CATALOG:
        ing_row = Ingredient(
            id=ing["id"],
            restaurant_id=DEFAULT_RESTAURANT_ID,
            name=ing["name"],
            category=ing["category"],
            unit=ing["unit"],
            unit_cost=ing["unit_cost"],
            shelf_life_days=ing["shelf_life_days"]
        )
        db.add(ing_row)
    db.commit()
    
    # 4. Recipe Items (Bill of Materials)
    for menu_id, ings in RECIPE_MAPPINGS.items():
        for r in ings:
            rec = RecipeItem(
                menu_item_id=menu_id,
                ingredient_id=r["ingredient_id"],
                quantity_required=r["qty"],
                unit="kg"
            )
            db.add(rec)
    db.commit()
    
    # 5. Inventory Items with realistic stock levels
    for ing in INGREDIENTS_CATALOG:
        inv = InventoryItem(
            branch_id=DEFAULT_BRANCH_ID,
            ingredient_id=ing["id"],
            current_stock=35.0 if "Dry" in ing["category"] else 18.0,
            safety_stock=10.0,
            reorder_point=22.0,
            unit=ing["unit"],
            expiry_date=date.today() + timedelta(days=ing["shelf_life_days"])
        )
        db.add(inv)
    db.commit()
    
    # 6. Generate 90 days of historical operational sales and waste records
    df_sales, df_waste = generate_synthetic_data(days=90)
    
    for _, row in df_sales.iterrows():
        sale = SalesRecord(
            branch_id=DEFAULT_BRANCH_ID,
            menu_item_id=row["menu_item_id"],
            sale_date=row["date"],
            sale_hour=19,
            quantity_sold=int(row["quantity_sold"]),
            unit_price=float(row["unit_price"]),
            total_amount=float(row["total_amount"]),
            promotion_active=bool(row["promotion_active"]),
            holiday_flag=bool(row["holiday_flag"]),
            weather_temp=float(row["weather_temp"]),
            rainfall_mm=float(row["rainfall_mm"]),
            weather_condition=str(row["weather_condition"]),
            source="pos_batch"
        )
        db.add(sale)
        
    for _, row in df_waste.iterrows():
        waste = WasteRecord(
            branch_id=DEFAULT_BRANCH_ID,
            menu_item_id=row["menu_item_id"],
            record_date=row["date"],
            prepared_quantity=int(row["prepared_quantity"]),
            sold_quantity=int(row["sold_quantity"]),
            remaining_quantity=int(row["remaining_quantity"]),
            wasted_quantity=int(row["wasted_quantity"]),
            waste_percentage=float(row["waste_percentage"]),
            waste_reason=str(row["waste_reason"]),
            cost_wasted=float(row["cost_wasted"]),
            notes="Standard kitchen shift log"
        )
        db.add(waste)
        
    # 7. Initial operational alert
    alert = Alert(
        branch_id=DEFAULT_BRANCH_ID,
        alert_type="high_waste_risk",
        severity="warning",
        title="Weekly Preparation Optimization",
        message="Historical over-production detected for Grilled Salmon on high-rain weekdays. Consider 15% batch trimming.",
        status="active"
    )
    db.add(alert)
    db.commit()
    print("Database seeding completed successfully.")
