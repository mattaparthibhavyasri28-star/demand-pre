import pytest
import pandas as pd
from backend.app.ml.dataset_generator import (
    generate_synthetic_data,
    MENU_ITEMS_CATALOG,
    INGREDIENTS_CATALOG
)
from backend.app.ml.feature_pipeline import (
    extract_features_df,
    prepare_training_tensors,
    build_single_inference_vector,
    FEATURE_COLUMNS
)

def test_synthetic_data_generator_shapes_and_columns():
    df_sales, df_waste = generate_synthetic_data(days=30, seed=123)
    
    assert len(df_sales) == 30 * len(MENU_ITEMS_CATALOG)
    assert len(df_waste) == 30 * len(MENU_ITEMS_CATALOG)
    
    expected_sales_cols = {
        "date", "menu_item_id", "menu_item_name", "category",
        "quantity_sold", "unit_price", "total_amount",
        "promotion_active", "holiday_flag", "weather_temp",
        "rainfall_mm", "weather_condition"
    }
    assert expected_sales_cols.issubset(set(df_sales.columns))
    assert (df_sales["quantity_sold"] >= 0).all()
    assert (df_waste["wasted_quantity"] >= 0).all()

def test_feature_pipeline_engineering():
    df_sales, _ = generate_synthetic_data(days=30, seed=99)
    df_feat = extract_features_df(df_sales)
    
    for col in FEATURE_COLUMNS:
        assert col in df_feat.columns, f"Missing feature column: {col}"
        
    # Check cyclical transforms are bounded [-1, 1]
    assert df_feat["sin_day_of_year"].between(-1.0, 1.0).all()
    assert df_feat["cos_day_of_year"].between(-1.0, 1.0).all()
    
    # Check lags are non-null
    assert not df_feat["sales_lag_1"].isna().any()
    assert not df_feat["sales_rolling_avg_7"].isna().any()

def test_inference_vector_builder():
    vec = build_single_inference_vector(
        menu_item_id="item-biryani-01",
        target_date="2026-10-10",
        unit_price=14.5,
        promotion_active=True,
        holiday_flag=False,
        festival_flag=True,
        weather_temp=28.0,
        rainfall_mm=12.5,
        recent_sales_history=[80, 85, 90, 75, 88, 92, 95]
    )
    assert vec.shape == (1, len(FEATURE_COLUMNS))
    assert not pd.isna(vec).any()
