"""
Realistic Synthetic Restaurant Dataset Generator
------------------------------------------------
Generates realistic multi-item, multi-feature daily restaurant sales,
weather conditions, holidays, promotions, and waste logs across 365 days.

Documented Limitation:
This dataset is synthetic and modeled for rigorous development, ML training,
and functional validation. Real restaurant POS data will vary in noise,
special local events, and kitchen practices.
"""

import math
import random
from datetime import date, timedelta
import pandas as pd
import numpy as np

MENU_ITEMS_CATALOG = [
    {
        "id": "item-biryani-01",
        "name": "Chicken Biryani",
        "category": "Main Course",
        "base_demand": 85,
        "price": 14.50,
        "prep_cost": 5.20,
        "shelf_life_hours": 12,
        "weekend_boost": 0.45,
        "rain_sensitivity": -0.15,
        "promo_boost": 0.30
    },
    {
        "id": "item-paneer-02",
        "name": "Paneer Butter Masala",
        "category": "Main Course",
        "base_demand": 60,
        "price": 12.00,
        "prep_cost": 3.80,
        "shelf_life_hours": 16,
        "weekend_boost": 0.35,
        "rain_sensitivity": 0.05, # Comfort food during rain
        "promo_boost": 0.25
    },
    {
        "id": "item-friedrice-03",
        "name": "Veg Fried Rice",
        "category": "Main Course",
        "base_demand": 50,
        "price": 9.50,
        "prep_cost": 2.50,
        "shelf_life_hours": 18,
        "weekend_boost": 0.20,
        "rain_sensitivity": -0.05,
        "promo_boost": 0.20
    },
    {
        "id": "item-salmon-04",
        "name": "Grilled Salmon",
        "category": "Main Course",
        "base_demand": 35,
        "price": 22.00,
        "prep_cost": 9.50,
        "shelf_life_hours": 8, # Highly perishable
        "weekend_boost": 0.50,
        "rain_sensitivity": -0.20,
        "promo_boost": 0.35
    },
    {
        "id": "item-pizza-05",
        "name": "Margherita Pizza",
        "category": "Main Course",
        "base_demand": 70,
        "price": 11.50,
        "prep_cost": 3.20,
        "shelf_life_hours": 24,
        "weekend_boost": 0.40,
        "rain_sensitivity": 0.10, # Delivery surge on rainy days
        "promo_boost": 0.40
    },
    {
        "id": "item-salad-06",
        "name": "Caesar Salad",
        "category": "Appetizer",
        "base_demand": 40,
        "price": 8.50,
        "prep_cost": 2.20,
        "shelf_life_hours": 14,
        "weekend_boost": 0.25,
        "rain_sensitivity": -0.25, # Hotter days demand salad, rainy days reduce it
        "promo_boost": 0.20
    }
]

INGREDIENTS_CATALOG = [
    {"id": "ing-chicken", "name": "Chicken Breast", "category": "Meat", "unit": "kg", "unit_cost": 6.50, "shelf_life_days": 4},
    {"id": "ing-rice", "name": "Basmati Rice", "category": "Dry Goods", "unit": "kg", "unit_cost": 2.20, "shelf_life_days": 90},
    {"id": "ing-paneer", "name": "Fresh Paneer", "category": "Dairy", "unit": "kg", "unit_cost": 5.00, "shelf_life_days": 5},
    {"id": "ing-salmon", "name": "Salmon Fillet", "category": "Seafood", "unit": "kg", "unit_cost": 18.00, "shelf_life_days": 3},
    {"id": "ing-flour", "name": "Pizza Flour", "category": "Dry Goods", "unit": "kg", "unit_cost": 1.50, "shelf_life_days": 60},
    {"id": "ing-cheese", "name": "Mozzarella Cheese", "category": "Dairy", "unit": "kg", "unit_cost": 7.00, "shelf_life_days": 14},
    {"id": "ing-lettuce", "name": "Romaine Lettuce", "category": "Produce", "unit": "kg", "unit_cost": 3.00, "shelf_life_days": 4},
    {"id": "ing-spices", "name": "Biryani & Masala Spices", "category": "Spices", "unit": "kg", "unit_cost": 12.00, "shelf_life_days": 180},
    {"id": "ing-butter", "name": "Cooking Butter", "category": "Dairy", "unit": "kg", "unit_cost": 4.50, "shelf_life_days": 30},
    {"id": "ing-veggies", "name": "Mixed Vegetables", "category": "Produce", "unit": "kg", "unit_cost": 2.50, "shelf_life_days": 5},
]

RECIPE_MAPPINGS = {
    "item-biryani-01": [
        {"ingredient_id": "ing-chicken", "qty": 0.30},
        {"ingredient_id": "ing-rice", "qty": 0.20},
        {"ingredient_id": "ing-spices", "qty": 0.03}
    ],
    "item-paneer-02": [
        {"ingredient_id": "ing-paneer", "qty": 0.25},
        {"ingredient_id": "ing-butter", "qty": 0.05},
        {"ingredient_id": "ing-spices", "qty": 0.02}
    ],
    "item-friedrice-03": [
        {"ingredient_id": "ing-rice", "qty": 0.20},
        {"ingredient_id": "ing-veggies", "qty": 0.15}
    ],
    "item-salmon-04": [
        {"ingredient_id": "ing-salmon", "qty": 0.25},
        {"ingredient_id": "ing-butter", "qty": 0.03}
    ],
    "item-pizza-05": [
        {"ingredient_id": "ing-flour", "qty": 0.20},
        {"ingredient_id": "ing-cheese", "qty": 0.15}
    ],
    "item-salad-06": [
        {"ingredient_id": "ing-lettuce", "qty": 0.20},
        {"ingredient_id": "ing-cheese", "qty": 0.04}
    ]
}

def generate_synthetic_data(days: int = 365, seed: int = 42) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generates two synchronized DataFrames:
    1. Daily Sales & Demand features
    2. Daily Kitchen Waste records
    """
    random.seed(seed)
    np.random.seed(seed)
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    sales_rows = []
    waste_rows = []
    
    # Pre-generate weather & holiday calendar
    calendar_dates = [start_date + timedelta(days=i) for i in range(days)]
    
    for current_date in calendar_dates:
        day_of_week = current_date.weekday() # 0 = Monday, 6 = Sunday
        is_weekend = day_of_week in [4, 5, 6] # Friday, Saturday, Sunday
        month = current_date.month
        
        # Weather simulation: Seasonality + stochastic shocks
        base_temp = 22.0 + 8.0 * math.sin((month - 3) * math.pi / 6)
        temp_shock = np.random.normal(0, 3.5)
        temperature = round(float(np.clip(base_temp + temp_shock, 5.0, 42.0)), 1)
        
        # Rainfall: higher probability in monsoon/autumn
        rain_prob = 0.35 if month in [6, 7, 8, 9] else 0.15
        is_rainy = random.random() < rain_prob
        rainfall_mm = round(float(np.random.exponential(15.0) if is_rainy else 0.0), 1)
        
        if rainfall_mm > 25.0:
            weather_condition = "Heavy Rain"
        elif rainfall_mm > 5.0:
            weather_condition = "Rain"
        elif rainfall_mm > 0.0:
            weather_condition = "Light Rain"
        elif temperature > 32.0:
            weather_condition = "Hot & Sunny"
        else:
            weather_condition = "Clear"
            
        # Holidays and Festivals
        is_holiday = (day_of_week in [5, 6] and random.random() < 0.10) or (random.random() < 0.03)
        is_festival = (month in [10, 11, 12] and random.random() < 0.08) or (random.random() < 0.02)
        
        for item in MENU_ITEMS_CATALOG:
            # Active promotion: random 12% probability
            promotion_active = random.random() < 0.12
            
            # Demand calculation with realistic response functions
            demand = item["base_demand"]
            
            # Weekend impact
            if is_weekend:
                weekend_mult = 1.0 + item["weekend_boost"] * (1.2 if day_of_week == 5 else 1.0)
                demand *= weekend_mult
                
            # Holiday & Festival multipliers
            if is_holiday:
                demand *= 1.25
            if is_festival:
                demand *= 1.35
                
            # Promotion effect
            if promotion_active:
                demand *= (1.0 + item["promo_boost"])
                
            # Weather effect
            if rainfall_mm > 5.0:
                demand *= (1.0 + item["rain_sensitivity"] * min(rainfall_mm / 20.0, 1.5))
            if temperature > 30.0 and item["name"] == "Caesar Salad":
                demand *= 1.20
            if temperature < 15.0 and item["name"] == "Chicken Biryani":
                demand *= 1.15
                
            # Random natural customer noise (+/- 12%)
            noise = np.random.normal(1.0, 0.08)
            quantity_sold = max(5, int(round(demand * noise)))
            
            total_amount = round(quantity_sold * item["price"], 2)
            
            sales_rows.append({
                "date": current_date,
                "menu_item_id": item["id"],
                "menu_item_name": item["name"],
                "category": item["category"],
                "quantity_sold": quantity_sold,
                "unit_price": item["price"],
                "total_amount": total_amount,
                "promotion_active": promotion_active,
                "holiday_flag": is_holiday,
                "festival_flag": is_festival,
                "weather_temp": temperature,
                "rainfall_mm": rainfall_mm,
                "weather_condition": weather_condition,
                "day_of_week": day_of_week,
                "is_weekend": is_weekend,
                "month": month
            })
            
            # Simulated preparation & waste logic
            # Without our system, kitchen cooks ~15-25% buffer above base or guesses incorrectly
            prep_bias = random.choice([1.08, 1.15, 1.22, 1.28])
            if is_rainy and item["rain_sensitivity"] < 0:
                # If kitchen didn't anticipate rain, they over-prepare significantly
                prep_bias += 0.15
                
            prepared_quantity = int(round(quantity_sold * prep_bias))
            remaining_quantity = max(0, prepared_quantity - quantity_sold)
            
            # Waste classification
            if remaining_quantity > 0:
                wasted_quantity = remaining_quantity
                
                # Determine primary waste reason based on item characteristics
                if remaining_quantity > 15:
                    waste_reason = "over_production"
                elif item["shelf_life_hours"] <= 8 and random.random() < 0.40:
                    waste_reason = "expired_shelf_life"
                elif random.random() < 0.20:
                    waste_reason = "preparation_error"
                elif random.random() < 0.25:
                    waste_reason = "customer_leftover"
                else:
                    waste_reason = "over_production"
            else:
                wasted_quantity = 0
                waste_reason = "none"
                
            waste_pct = round((wasted_quantity / prepared_quantity) * 100, 2) if prepared_quantity > 0 else 0.0
            cost_wasted = round(wasted_quantity * item["prep_cost"], 2)
            
            waste_rows.append({
                "date": current_date,
                "menu_item_id": item["id"],
                "menu_item_name": item["name"],
                "prepared_quantity": prepared_quantity,
                "sold_quantity": quantity_sold,
                "remaining_quantity": remaining_quantity,
                "wasted_quantity": wasted_quantity,
                "waste_percentage": waste_pct,
                "waste_reason": waste_reason,
                "cost_wasted": cost_wasted,
                "prep_cost": item["prep_cost"]
            })
            
    df_sales = pd.DataFrame(sales_rows)
    df_waste = pd.DataFrame(waste_rows)
    
    return df_sales, df_waste

if __name__ == "__main__":
    df_s, df_w = generate_synthetic_data(days=365)
    print(f"Generated {len(df_s)} sales rows and {len(df_w)} waste rows across 365 days.")
    print(df_s.head(3))
