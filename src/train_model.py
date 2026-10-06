"""Train and compare beginner-friendly regression models chronologically."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeRegressor

from src.feature_engineering import (
    CATEGORICAL_FEATURES, FEATURE_COLUMNS, NUMERIC_FEATURES, TARGET_COLUMN,
    add_historical_features,
)

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "demand_model.pkl"


def _pipeline(model: Any, scale_numeric: bool = False) -> Pipeline:
    numeric_steps = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        numeric_steps.append(("scaler", StandardScaler()))
    prep = ColumnTransformer([
        ("numeric", Pipeline(numeric_steps), NUMERIC_FEATURES),
        ("categorical", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]), CATEGORICAL_FEATURES),
    ])
    return Pipeline([("preprocessor", prep), ("model", model)])


def chronological_split(featured: pd.DataFrame, test_fraction: float = 0.2):
    dates = np.array(sorted(featured["date"].unique()))
    if len(dates) < 10:
        raise ValueError("At least 10 distinct dates with complete history are needed to train.")
    split_at = max(1, int(len(dates) * (1 - test_fraction)))
    split_date = dates[split_at]
    train = featured[featured["date"] < split_date]
    test = featured[featured["date"] >= split_date]
    if train.empty or test.empty:
        raise ValueError("Not enough date history for a chronological train/test split.")
    return train, test


def regression_metrics(actual, predicted) -> dict[str, float]:
    return {
        "MAE": float(mean_absolute_error(actual, predicted)),
        "MSE": float(mean_squared_error(actual, predicted)),
        "RMSE": float(np.sqrt(mean_squared_error(actual, predicted))),
        "R²": float(r2_score(actual, predicted)) if len(actual) > 1 else 0.0,
    }


def train_and_compare(frame: pd.DataFrame, model_path: Path | str = MODEL_PATH):
    featured = add_historical_features(frame)
    train, test = chronological_split(featured)
    estimators = {
        "Linear Regression": (LinearRegression(), True),
        "Decision Tree": (DecisionTreeRegressor(max_depth=8, min_samples_leaf=3, random_state=42), False),
        "Random Forest": (RandomForestRegressor(n_estimators=120, max_depth=12, min_samples_leaf=2,
                                                  random_state=42, n_jobs=-1), False),
        "Gradient Boosting": (GradientBoostingRegressor(n_estimators=100, max_depth=3,
                                                         learning_rate=0.06, random_state=42), False),
    }
    results, fitted, predictions = [], {}, {}
    for name, (estimator, scale) in estimators.items():
        pipeline = _pipeline(estimator, scale)
        pipeline.fit(train[FEATURE_COLUMNS], train[TARGET_COLUMN])
        values = np.maximum(0, pipeline.predict(test[FEATURE_COLUMNS]))
        metrics = regression_metrics(test[TARGET_COLUMN], values)
        results.append({"Model": name, **metrics})
        fitted[name] = pipeline
        predictions[name] = values
    comparison = pd.DataFrame(results).sort_values("MAE").reset_index(drop=True)
    winner = str(comparison.iloc[0]["Model"])
    artifact = {
        "model": fitted[winner], "model_name": winner,
        "feature_columns": FEATURE_COLUMNS,
        "training_end_date": str(train["date"].max().date()),
        "validation_start_date": str(test["date"].min().date()),
        "validation_metrics": comparison.iloc[0].to_dict(),
        "data_note": "Validation uses a chronological holdout. Dataset provenance should be reported by the caller.",
    }
    path = Path(model_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, path)
    validation = test[["date", "menu_item", "meal_type", TARGET_COLUMN,
                       "prepared_quantity", "price"]].copy()
    validation["predicted_demand"] = predictions[winner]
    return artifact, comparison, validation


def main() -> None:
    """Train from the bundled CSV and print the chronological holdout results."""
    from src.data_preprocessing import load_sales_data

    data_path = Path(__file__).resolve().parents[1] / "data" / "restaurant_sales.csv"
    frame = load_sales_data(data_path)
    artifact, comparison, validation = train_and_compare(frame)
    print(f"Selected model: {artifact['model_name']}")
    print(f"Saved model: {MODEL_PATH}")
    print(f"Training ends: {artifact['training_end_date']}")
    print(f"Validation starts: {artifact['validation_start_date']}")
    print(f"Validation rows: {len(validation)}")
    print(comparison.to_string(index=False))


if __name__ == "__main__":
    main()
