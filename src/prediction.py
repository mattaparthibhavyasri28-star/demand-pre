"""Load the locally trained model and forecast a selected future item/meal."""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.feature_engineering import features_for_future
from src.train_model import MODEL_PATH


def predict_demand(frame: pd.DataFrame, target_date, menu_item: str, meal_type: str,
                   model_path: Path | str = MODEL_PATH,
                   holiday_event: bool | None = None) -> float:
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError("The local model is missing. Train the model before predicting.")
    artifact = joblib.load(path)
    row = features_for_future(frame, pd.Timestamp(target_date), menu_item, meal_type, holiday_event)
    return float(max(0, np.asarray(artifact["model"].predict(row)).ravel()[0]))
