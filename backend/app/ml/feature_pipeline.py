"""
Feature Engineering Pipeline
----------------------------
Transforms raw tabular sales and environmental records into model-ready
numerical tensors with lag indicators, calendar encodings, and weather features.
"""

import math
from typing import List, Tuple, Dict, Any
import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "item_code", # Integer-encoded menu item
    "day_of_week",
    "is_weekend",
    "month",
    "sin_day_of_year",
    "cos_day_of_year",
    "unit_price",
    "promotion_active",
    "holiday_flag",
    "festival_flag",
    "weather_temp",
    "rainfall_mm",
    "is_rainy",
    "sales_lag_1",
    "sales_lag_7",
    "sales_rolling_avg_7",
    "sales_rolling_std_7"
]

ITEM_TO_CODE = {
    "item-biryani-01": 0,
    "item-paneer-02": 1,
    "item-friedrice-03": 2,
    "item-salmon-04": 3,
    "item-pizza-05": 4,
    "item-salad-06": 5
}

def extract_features_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enriches raw sales dataframe with time-series lag and rolling statistics per item.
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by=["menu_item_id", "date"]).reset_index(drop=True)
    
    # Encode item code
    df["item_code"] = df["menu_item_id"].map(lambda x: ITEM_TO_CODE.get(x, 0))
    
    # Cyclical date transformations
    day_of_year = df["date"].dt.dayofyear
    df["sin_day_of_year"] = np.sin(2 * np.pi * day_of_year / 365.25)
    df["cos_day_of_year"] = np.cos(2 * np.pi * day_of_year / 365.25)
    
    df["day_of_week"] = df["date"].dt.weekday
    df["is_weekend"] = df["day_of_week"].isin([4, 5, 6]).astype(int)
    df["month"] = df["date"].dt.month
    
    # Binary flags
    df["promotion_active"] = df["promotion_active"].astype(int)
    df["holiday_flag"] = df["holiday_flag"].astype(int)
    df["festival_flag"] = df["festival_flag"].astype(int)
    df["is_rainy"] = (df["rainfall_mm"] > 1.0).astype(int)
    
    # Impute missing weather values
    df["weather_temp"] = df["weather_temp"].fillna(24.0)
    df["rainfall_mm"] = df["rainfall_mm"].fillna(0.0)
    
    # Group by item to create reliable lag features
    grouped = df.groupby("menu_item_id")
    
    df["sales_lag_1"] = grouped["quantity_sold"].shift(1)
    df["sales_lag_7"] = grouped["quantity_sold"].shift(7)
    df["sales_rolling_avg_7"] = grouped["quantity_sold"].transform(
        lambda s: s.shift(1).rolling(window=7, min_periods=1).mean()
    )
    df["sales_rolling_std_7"] = grouped["quantity_sold"].transform(
        lambda s: s.shift(1).rolling(window=7, min_periods=1).std()
    )
    
    # Fill NA from shifts with item-level mean/median
    df["sales_lag_1"] = df["sales_lag_1"].fillna(df["quantity_sold"])
    df["sales_lag_7"] = df["sales_lag_7"].fillna(df["quantity_sold"])
    df["sales_rolling_avg_7"] = df["sales_rolling_avg_7"].fillna(df["quantity_sold"])
    df["sales_rolling_std_7"] = df["sales_rolling_std_7"].fillna(2.0)
    
    return df

def prepare_training_tensors(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """
    Transforms dataframe into X feature matrix, y target vector, and feature column names.
    """
    df_feat = extract_features_df(df)
    X = df_feat[FEATURE_COLUMNS].values
    y = df_feat["quantity_sold"].values
    return X, y, FEATURE_COLUMNS

def build_single_inference_vector(
    menu_item_id: str,
    target_date: Any,
    unit_price: float,
    promotion_active: bool,
    holiday_flag: bool,
    festival_flag: bool,
    weather_temp: float,
    rainfall_mm: float,
    recent_sales_history: List[int] = None
) -> np.ndarray:
    """
    Constructs a single 1xD feature vector for real-time item prediction.
    """
    target_dt = pd.to_datetime(target_date)
    item_code = ITEM_TO_CODE.get(menu_item_id, 0)
    
    day_of_week = target_dt.weekday()
    is_weekend = 1 if day_of_week in [4, 5, 6] else 0
    month = target_dt.month
    day_of_year = target_dt.dayofyear
    
    sin_day = float(np.sin(2 * np.pi * day_of_year / 365.25))
    cos_day = float(np.cos(2 * np.pi * day_of_year / 365.25))
    
    is_rainy = 1 if rainfall_mm > 1.0 else 0
    
    # Recent sales lags
    if recent_sales_history and len(recent_sales_history) >= 1:
        lag_1 = float(recent_sales_history[-1])
        lag_7 = float(recent_sales_history[-7]) if len(recent_sales_history) >= 7 else lag_1
        avg_7 = float(np.mean(recent_sales_history[-7:]))
        std_7 = float(np.std(recent_sales_history[-7:])) if len(recent_sales_history) >= 2 else 2.0
    else:
        # Fallback to reasonable defaults from item catalog
        base_estimate = 50.0
        lag_1 = base_estimate
        lag_7 = base_estimate
        avg_7 = base_estimate
        std_7 = 5.0
        
    vector = [
        item_code,
        day_of_week,
        is_weekend,
        month,
        sin_day,
        cos_day,
        unit_price,
        1 if promotion_active else 0,
        1 if holiday_flag else 0,
        1 if festival_flag else 0,
        float(weather_temp),
        float(rainfall_mm),
        is_rainy,
        lag_1,
        lag_7,
        avg_7,
        std_7
    ]
    return np.array([vector], dtype=np.float32)
