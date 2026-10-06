"""Offline Streamlit dashboard for restaurant demand and waste planning."""

from __future__ import annotations

import hashlib
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from src.data_preprocessing import cleaning_summary, load_sales_data
from src.prediction import predict_demand
from src.train_model import MODEL_PATH, train_and_compare
from src.recommendations import preparation_recommendation

ROOT = Path(__file__).resolve().parent
DEFAULT_DATA = ROOT / "data" / "restaurant_sales.csv"

st.set_page_config(page_title="Restaurant Demand & Waste Planner", page_icon="🥗",
                   layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
  .stApp {background: #f5f7f4}
  [data-testid="stMetric"] {background:#fff;padding:16px;border:1px solid #e5e9e4;border-radius:14px}
  .hero {padding:1.5rem 1.8rem;background:linear-gradient(115deg,#123b32,#23745e);border-radius:18px;color:white;margin-bottom:1rem}
  .hero p {color:#d8eee4;margin-bottom:0}
  section[data-testid="stSidebar"] {background:#eef3ed}
</style>
""", unsafe_allow_html=True)
sns.set_theme(style="whitegrid", palette="crest")

st.markdown("<div class='hero'><h1>🥗 Restaurant Demand & Waste Planner</h1><p>Use historical sales to plan food preparation with a locally trained model. No external APIs or API keys.</p></div>", unsafe_allow_html=True)
st.caption("B.Tech IT project · Offline demo data is synthetic. Replace it with your restaurant's authorized sales export before making operational decisions.")

with st.sidebar:
    st.header("Data source")
    uploaded = st.file_uploader("Upload restaurant sales CSV", type=["csv"], help="Required: date, menu_item, meal_type, price, quantity_sold, customers. Optional: prepared_quantity, holiday_event.")
    st.markdown("**Expected columns**")
    st.code("date, menu_item, meal_type, price, quantity_sold, customers", language="text")
    st.caption("This app does not call POS, weather, LLM, mapping, or other external APIs.")

try:
    source = uploaded if uploaded is not None else DEFAULT_DATA
    frame = load_sales_data(source)
except Exception as exc:
    st.error(f"Could not load the dataset: {exc}")
    st.stop()

source_hash = hashlib.sha256(frame.to_csv(index=False).encode("utf-8")).hexdigest()
if st.session_state.get("data_hash") != source_hash:
    with st.spinner("Training and comparing four models on a chronological holdout…"):
        try:
            artifact, comparison, validation = train_and_compare(frame, MODEL_PATH)
            st.session_state.update(data_hash=source_hash, clean_frame=frame,
                                    artifact=artifact, comparison=comparison,
                                    validation=validation)
        except Exception as exc:
            st.error(f"Model training failed: {exc}")
            st.info("Check that the CSV has enough valid history and that project dependencies are installed.")
            st.stop()

frame = st.session_state.clean_frame
artifact = st.session_state.artifact
comparison = st.session_state.comparison
validation = st.session_state.validation
cleaning = cleaning_summary(frame)

overview, analysis, forecast_tab, models_tab = st.tabs([
    "Overview & Data", "Sales Analysis", "Demand Planning", "Model Evaluation"
])

with overview:
    st.subheader("Dataset preview")
    st.dataframe(frame.head(20), use_container_width=True, hide_index=True)
    a, b, c, d = st.columns(4)
    a.metric("Valid sales records", f"{len(frame):,}")
    b.metric("Menu items", f"{frame.menu_item.nunique():,}")
    c.metric("Date coverage", f"{frame.date.min():%d %b %Y} – {frame.date.max():%d %b %Y}")
    d.metric("Average portions sold", f"{frame.quantity_sold.mean():.1f}")
    st.markdown("#### Data cleaning summary")
    cc1, cc2, cc3 = st.columns(3)
    cc1.metric("Rows read", f"{cleaning['input_rows']:,}")
    cc2.metric("Rows retained", f"{cleaning['valid_rows']:,}")
    cc3.metric("Invalid or duplicate rows removed", f"{cleaning['removed_rows']:,}")
    st.caption("Rows with invalid dates, blank categories, non-positive prices, or negative/missing sales/customer counts are excluded. Missing prepared quantity is set to observed sales for waste-estimation purposes.")

with analysis:
    st.subheader("Sales patterns")
    daily = frame.groupby("date", as_index=False).agg(quantity_sold=("quantity_sold", "sum"), customers=("customers", "sum"))
    fig, ax = plt.subplots(figsize=(11, 4))
    sns.lineplot(data=daily, x="date", y="quantity_sold", ax=ax, linewidth=1.8)
    ax.set(title="Daily portions sold", xlabel="Date", ylabel="Portions")
    st.pyplot(fig, use_container_width=True)
    left, right = st.columns(2)
    with left:
        by_item = frame.groupby("menu_item", as_index=False)["quantity_sold"].mean().sort_values("quantity_sold", ascending=False)
        fig, ax = plt.subplots(figsize=(7, 4))
        sns.barplot(data=by_item, x="quantity_sold", y="menu_item", ax=ax)
        ax.set(title="Average portions by menu item", xlabel="Average portions", ylabel="")
        st.pyplot(fig, use_container_width=True)
    with right:
        by_weekday = frame.assign(day=frame.date.dt.day_name()).groupby("day", as_index=False)["quantity_sold"].mean()
        order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        by_weekday["day"] = pd.Categorical(by_weekday.day, categories=order, ordered=True)
        fig, ax = plt.subplots(figsize=(7, 4))
        sns.barplot(data=by_weekday.sort_values("day"), x="day", y="quantity_sold", ax=ax)
        ax.tick_params(axis="x", rotation=30)
        ax.set(title="Average portions by weekday", xlabel="", ylabel="Average portions")
        st.pyplot(fig, use_container_width=True)

with forecast_tab:
    st.subheader("Plan a future service")
    items = sorted(frame.menu_item.unique().tolist())
    item = st.selectbox("Menu item", items)
    meals = sorted(frame.loc[frame.menu_item == item, "meal_type"].unique().tolist())
    meal = st.selectbox("Meal / service", meals)
    next_history_day = (frame.date.max() + pd.Timedelta(days=1)).date()
    future_min = max(next_history_day, pd.Timestamp.today().date())
    target = st.date_input("Forecast date", value=future_min, min_value=future_min)
    holiday_event = st.checkbox("Holiday or local event expected", value=False)
    recent = frame[(frame.menu_item == item) & (frame.meal_type == meal)].sort_values("date").tail(7)
    prepared_default = int(round(recent.quantity_sold.mean())) if not recent.empty else 0
    prepared = st.number_input("Current planned preparation (portions)", min_value=0,
                               value=max(0, prepared_default), step=1)
    if st.button("Predict demand", type="primary", use_container_width=False):
        try:
            demand = predict_demand(frame, pd.Timestamp(target), item, meal,
                                    holiday_event=holiday_event)
            advice = preparation_recommendation(demand, int(prepared))
            st.session_state.last_prediction = {"date": str(target), "menu_item": item,
                "meal_type": meal, "predicted_demand": round(demand, 2),
                "prepared_quantity": int(prepared), **advice}
        except Exception as exc:
            st.error(f"Prediction could not be created: {exc}")
    result = st.session_state.get("last_prediction")
    if result:
        p1, p2, p3 = st.columns(3)
        p1.metric("Predicted demand", f"{result['predicted_demand']:.1f} portions")
        p2.metric("Estimated excess food", f"{result['excess_food']:.1f} portions")
        p3.metric("Estimated wastage", f"{result['estimated_wastage_percentage']:.1f}%")
        st.success(result["recommendation"])
        st.info(result["explanation"])
        st.caption(f"Model: {artifact['model_name']} · Future prediction from local sales history. It is an estimate, not a guarantee; no calibrated prediction interval is currently provided.")
        download_row = pd.DataFrame([result])
        st.download_button("Download this prediction as CSV", download_row.to_csv(index=False),
                           file_name="demand_prediction.csv", mime="text/csv")
    st.markdown("#### Validation: actual vs predicted")
    plot_data = validation.copy().sort_values("date")
    selected_validation = plot_data[(plot_data.menu_item == item) & (plot_data.meal_type == meal)]
    if not selected_validation.empty:
        fig, ax = plt.subplots(figsize=(11, 4))
        ax.plot(selected_validation.date, selected_validation.quantity_sold, label="Actual", linewidth=1.7)
        ax.plot(selected_validation.date, selected_validation.predicted_demand, label="Predicted", linewidth=1.7)
        ax.set(title=f"Chronological holdout · {item} · {meal}", xlabel="Date", ylabel="Portions")
        ax.legend()
        st.pyplot(fig, use_container_width=True)

with models_tab:
    st.subheader("Chronological model comparison")
    st.caption(f"Training data ends {artifact['training_end_date']}; validation begins {artifact['validation_start_date']}. Historical lag features use earlier sales only.")
    display_comparison = comparison.copy()
    for column in ["MAE", "MSE", "RMSE", "R²"]:
        display_comparison[column] = display_comparison[column].round(3)
    st.dataframe(display_comparison, use_container_width=True, hide_index=True)
    st.success(f"Selected by lowest chronological holdout MAE: **{artifact['model_name']}**")
    winner = display_comparison.iloc[0]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("MAE", f"{winner.MAE:.2f} portions")
    m2.metric("MSE", f"{winner.MSE:.2f}")
    m3.metric("RMSE", f"{winner.RMSE:.2f} portions")
    m4.metric("R²", f"{winner['R²']:.3f}")
    st.download_button("Download validation predictions", validation.to_csv(index=False),
                       file_name="validation_predictions.csv", mime="text/csv")
    st.caption("Metrics describe only this dataset's chronological holdout. Synthetic demo data cannot establish real restaurant accuracy or food-waste savings.")
