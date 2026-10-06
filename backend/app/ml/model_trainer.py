"""
Model Training and Comparative Evaluation Engine
------------------------------------------------
Trains, validates, and compares four baseline-to-advanced regression models:
1. Linear Regression
2. Random Forest Regressor
3. Gradient Boosting Regressor
4. XGBoost Regressor

Calculates MAE, RMSE, MAPE, and R2 on a chronological holdout test set.
Selects the top-performing model and persists it to disk along with validation metrics.
"""

import json
from pathlib import Path
from typing import Dict, Any, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from backend.app.config import settings
from backend.app.ml.dataset_generator import generate_synthetic_data
from backend.app.ml.feature_pipeline import (
    prepare_training_tensors,
    FEATURE_COLUMNS,
    extract_features_df
)

def mean_absolute_percentage_error_safe(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Safe MAPE avoiding division by zero."""
    y_true_safe = np.where(y_true == 0, 1.0, y_true)
    return float(np.mean(np.abs((y_true - y_pred) / y_true_safe)) * 100)

def train_and_evaluate_all_models(
    df_sales: pd.DataFrame = None,
    test_split_ratio: float = 0.20
) -> Dict[str, Any]:
    """
    Trains 4 candidate models, compares metrics, and saves the winner.
    """
    if df_sales is None:
        # Generate full year benchmark dataset
        df_sales, df_waste = generate_synthetic_data(days=365)
        # Save raw datasets to data/
        data_dir = settings.DATA_DIR
        data_dir.mkdir(parents=True, exist_ok=True)
        df_sales.to_csv(data_dir / "sample_restaurant_sales.csv", index=False)
        df_waste.to_csv(data_dir / "sample_restaurant_waste.csv", index=False)
        
    df_feat = extract_features_df(df_sales)
    
    # Chronological train/test split to preserve temporal sequence
    unique_dates = sorted(df_feat["date"].unique())
    split_idx = int(len(unique_dates) * (1.0 - test_split_ratio))
    split_date = unique_dates[split_idx]
    
    train_mask = df_feat["date"] < split_date
    test_mask = df_feat["date"] >= split_date
    
    X_train = df_feat.loc[train_mask, FEATURE_COLUMNS].values
    y_train = df_feat.loc[train_mask, "quantity_sold"].values
    
    X_test = df_feat.loc[test_mask, FEATURE_COLUMNS].values
    y_test = df_feat.loc[test_mask, "quantity_sold"].values
    
    candidates = {
        "LinearRegression": LinearRegression(),
        "RandomForest": RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1),
        "GradientBoosting": GradientBoostingRegressor(n_estimators=100, max_depth=5, learning_rate=0.08, random_state=42),
        "XGBoost": XGBRegressor(n_estimators=120, max_depth=5, learning_rate=0.08, random_state=42, n_jobs=-1)
    }
    
    model_results = {}
    fitted_models = {}
    
    for name, model in candidates.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        mae = float(mean_absolute_error(y_test, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        mape = float(mean_absolute_percentage_error_safe(y_test, y_pred))
        r2 = float(r2_score(y_test, y_pred))
        
        fitted_models[name] = model
        model_results[name] = {
            "mae": round(mae, 3),
            "rmse": round(rmse, 3),
            "mape": round(mape, 2),
            "r2_score": round(r2, 4),
            "sample_count": len(y_test)
        }
        
    # Select best model based on lowest MAE and highest R2
    best_model_name = min(model_results, key=lambda k: model_results[k]["mae"])
    best_model = fitted_models[best_model_name]
    
    # Extract feature importances if available
    feature_importances = {}
    if hasattr(best_model, "feature_importances_"):
        raw_imp = best_model.feature_importances_
        sum_imp = float(np.sum(raw_imp)) if np.sum(raw_imp) > 0 else 1.0
        for col, imp in zip(FEATURE_COLUMNS, raw_imp):
            feature_importances[col] = round(float(imp / sum_imp), 4)
    elif hasattr(best_model, "coef_"):
        raw_coef = np.abs(best_model.coef_)
        sum_coef = float(np.sum(raw_coef)) if np.sum(raw_coef) > 0 else 1.0
        for col, coef in zip(FEATURE_COLUMNS, raw_coef):
            feature_importances[col] = round(float(coef / sum_coef), 4)
            
    # Persist the best model and artifact metadata
    models_dir = settings.TRAINED_MODELS_DIR
    models_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = models_dir / "best_model.joblib"
    joblib.dump({
        "model": best_model,
        "model_name": best_model_name,
        "feature_columns": FEATURE_COLUMNS,
        "metrics": model_results[best_model_name],
        "all_candidate_metrics": model_results,
        "feature_importances": feature_importances,
        "version": "1.0.0"
    }, model_path)
    
    metrics_path = models_dir / "model_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump({
            "selected_model": best_model_name,
            "version": "1.0.0",
            "candidates": model_results,
            "feature_importances": feature_importances,
            "train_samples": len(y_train),
            "test_samples": len(y_test)
        }, f, indent=2)
        
    return {
        "selected_model": best_model_name,
        "version": "1.0.0",
        "candidates": model_results,
        "feature_importances": feature_importances,
        "train_samples": len(y_train),
        "test_samples": len(y_test)
    }

if __name__ == "__main__":
    summary = train_and_evaluate_all_models()
    print("Model Training & Validation Complete:")
    print(json.dumps(summary, indent=2))
