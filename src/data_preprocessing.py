"""Load and clean restaurant sales data without using external services."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

REQUIRED_COLUMNS = {
    "date", "menu_item", "meal_type", "price", "quantity_sold", "customers"
}
OPTIONAL_COLUMNS = {"prepared_quantity", "holiday_event"}


def load_sales_data(source: Any) -> pd.DataFrame:
    """Read a CSV path or uploaded file and return a cleaned dataframe."""
    if isinstance(source, (str, Path)):
        frame = pd.read_csv(source)
    else:
        # Streamlit UploadedFile is file-like; rewind in case it was previewed.
        if hasattr(source, "seek"):
            source.seek(0)
        frame = pd.read_csv(source)
    return clean_sales_data(frame)


def clean_sales_data(frame: pd.DataFrame) -> pd.DataFrame:
    """Standardize columns, validate records, and report-friendly clean rows."""
    if frame.empty:
        raise ValueError("The uploaded CSV has no data rows.")

    df = frame.copy()
    df.columns = [str(column).strip().lower().replace(" ", "_") for column in df.columns]
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))

    df["date"] = pd.to_datetime(df["date"], errors="coerce", format="mixed")
    for column in ("price", "quantity_sold", "customers"):
        df[column] = pd.to_numeric(df[column], errors="coerce")

    for column in OPTIONAL_COLUMNS:
        if column not in df.columns:
            df[column] = 0 if column == "prepared_quantity" else False
    df["prepared_quantity"] = pd.to_numeric(df["prepared_quantity"], errors="coerce")
    df["holiday_event"] = df["holiday_event"].fillna(False).astype(str).str.lower().isin(
        {"true", "1", "yes", "y"}
    )

    df["menu_item"] = df["menu_item"].astype("string").str.strip()
    df["meal_type"] = df["meal_type"].astype("string").str.strip()
    before = len(df)
    valid = (
        df["date"].notna()
        & df["menu_item"].notna() & df["menu_item"].ne("")
        & df["meal_type"].notna() & df["meal_type"].ne("")
        & df["price"].notna() & df["price"].gt(0)
        & df["quantity_sold"].notna() & df["quantity_sold"].ge(0)
        & df["customers"].notna() & df["customers"].ge(0)
    )
    df = df.loc[valid].copy()
    valid_rows = len(df)
    df["prepared_quantity"] = df["prepared_quantity"].fillna(df["quantity_sold"])
    df["prepared_quantity"] = df["prepared_quantity"].clip(lower=0)
    df["quantity_sold"] = df["quantity_sold"].round().astype(int)
    df["customers"] = df["customers"].round().astype(int)
    df["prepared_quantity"] = df["prepared_quantity"].round().astype(int)
    df["date"] = df["date"].dt.normalize()
    df = df.sort_values(["menu_item", "meal_type", "date"]).drop_duplicates(
        ["date", "menu_item", "meal_type"], keep="last"
    ).reset_index(drop=True)
    df.attrs["cleaning_summary"] = {
        "input_rows": before,
        "valid_rows": len(df),
        "removed_rows": before - len(df),
        "duplicate_rows_removed": valid_rows - len(df),
    }
    if df.empty:
        raise ValueError("No valid rows remain. Check dates, item names, prices and quantities.")
    return df


def cleaning_summary(frame: pd.DataFrame) -> dict[str, int]:
    return dict(frame.attrs.get("cleaning_summary", {
        "input_rows": len(frame), "valid_rows": len(frame), "removed_rows": 0,
        "duplicate_rows_removed": 0,
    }))
