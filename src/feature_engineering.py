"""Create calendar and leakage-safe historical sales features."""

from __future__ import annotations

import pandas as pd

NUMERIC_FEATURES = [
    "day_of_week", "month", "is_weekend", "previous_sales",
    "sales_7_days_ago", "rolling_mean_7", "price", "customers_prior_7", "holiday_event",
]
CATEGORICAL_FEATURES = ["meal_type", "menu_item"]
FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET_COLUMN = "quantity_sold"


def add_historical_features(frame: pd.DataFrame, drop_incomplete: bool = True) -> pd.DataFrame:
    """Lag/rolling fields use only earlier observations for the same item and meal."""
    df = frame.sort_values(["menu_item", "meal_type", "date"]).copy()
    group = df.groupby(["menu_item", "meal_type"], sort=False)[TARGET_COLUMN]
    df["previous_sales"] = group.shift(1)
    df["sales_7_days_ago"] = group.shift(7)
    df["rolling_mean_7"] = group.transform(lambda values: values.shift(1).rolling(7, min_periods=7).mean())
    df["customers_prior_7"] = df.groupby(["menu_item", "meal_type"], sort=False)["customers"].transform(
        lambda values: values.shift(1).rolling(7, min_periods=7).mean()
    )
    df["day_of_week"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
    df["holiday_event"] = df["holiday_event"].astype(int)
    if drop_incomplete:
        df = df.dropna(subset=["previous_sales", "sales_7_days_ago", "rolling_mean_7", "customers_prior_7"])
    return df


def features_for_future(frame: pd.DataFrame, target_date: pd.Timestamp,
                        menu_item: str, meal_type: str,
                        holiday_event: bool | None = None) -> pd.DataFrame:
    """Build one future feature row from the last seven known sales records."""
    history = frame[(frame["menu_item"] == menu_item) & (frame["meal_type"] == meal_type)]
    history = history[history["date"] < target_date].sort_values("date")
    if len(history) < 7:
        raise ValueError("At least 7 prior sales records are required for this item and meal.")
    last = history.iloc[-1]
    d = pd.Timestamp(target_date)
    return pd.DataFrame([{
        "day_of_week": d.dayofweek,
        "month": d.month,
        "is_weekend": int(d.dayofweek in (5, 6)),
        "previous_sales": float(last["quantity_sold"]),
        "sales_7_days_ago": float(history.iloc[-7]["quantity_sold"]),
        "rolling_mean_7": float(history.tail(7)["quantity_sold"].mean()),
        "price": float(last["price"]),
        "customers_prior_7": float(history.tail(7)["customers"].mean()),
        "holiday_event": int(last["holiday_event"] if holiday_event is None else holiday_event),
        "meal_type": meal_type,
        "menu_item": menu_item,
    }], columns=FEATURE_COLUMNS)
