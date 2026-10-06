import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base
from backend.app.models.entities import *
from backend.app.services.seed_data import seed_database_if_empty, DEFAULT_BRANCH_ID
from backend.app.services.demand_forecasting import (
    forecast_single_item,
    update_prediction_near_real_time,
    get_loaded_model
)
from backend.app.services.inventory_optimizer import calculate_inventory_requirements
from backend.app.services.waste_analyzer import log_waste_entry, get_waste_analytics
from backend.app.services.what_if_simulator import run_what_if_simulation
from backend.app.services.alert_engine import evaluate_and_generate_alerts, acknowledge_alert
from backend.app.services.donation_workflow import (
    detect_surplus_candidates,
    register_food_safe_donation,
    list_branch_donations
)
from backend.app.services.sustainability_calc import calculate_sustainability_metrics
from backend.app.schemas.waste import WasteLogCreate
from backend.app.schemas.simulation import WhatIfSimulationRequest
from backend.app.schemas.donation import FoodSafetyCertificationRequest

@pytest.fixture(scope="module")
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSession()
    seed_database_if_empty(db)
    yield db
    db.close()

def test_ml_model_and_forecast_inference(test_db):
    artifact = get_loaded_model()
    assert artifact is not None
    assert "metrics" in artifact
    assert artifact["metrics"]["r2_score"] > 0.80
    assert artifact["metrics"]["mae"] < 10.0
    
    # Forecast an item
    res = forecast_single_item(
        db=test_db,
        branch_id=DEFAULT_BRANCH_ID,
        menu_item_id="item-biryani-01",
        target_date=date.today(),
        weather_temp=26.0,
        rainfall_mm=0.0
    )
    assert res.predicted_demand > 0
    assert res.confidence_lower <= res.predicted_demand <= res.confidence_upper
    assert res.recommended_preparation >= int(res.predicted_demand)
    assert len(res.feature_contributions) >= 1

def test_near_real_time_updating(test_db):
    # Morning: cumulative sales = 15
    res_morning = update_prediction_near_real_time(
        db=test_db,
        branch_id=DEFAULT_BRANCH_ID,
        menu_item_id="item-biryani-01",
        target_date=date.today(),
        current_hour=11,
        cumulative_sales=15
    )
    assert res_morning.updated_predicted_total >= 15
    
    # Surging lunch: cumulative sales = 65 by 13:00
    res_surge = update_prediction_near_real_time(
        db=test_db,
        branch_id=DEFAULT_BRANCH_ID,
        menu_item_id="item-biryani-01",
        target_date=date.today(),
        current_hour=13,
        cumulative_sales=65
    )
    assert res_surge.status_assessment == "surging_demand"
    assert res_surge.recommended_additional_prep > 0

def test_smart_inventory_requirements(test_db):
    inv_res = calculate_inventory_requirements(
        db=test_db,
        branch_id=DEFAULT_BRANCH_ID,
        planning_date=date.today()
    )
    assert len(inv_res.recommendations) > 0
    assert inv_res.total_estimated_purchase_cost >= 0
    
    # Check safety stock and recommendation formula
    for req in inv_res.recommendations:
        assert req.safety_stock > 0
        expected_deficit = round((req.predicted_demand_consumption + req.safety_stock) - req.current_stock, 2)
        assert req.net_deficit == expected_deficit
        assert req.recommended_purchase == max(0.0, expected_deficit)

def test_waste_tracking_and_root_cause_analysis(test_db):
    entry = WasteLogCreate(
        branch_id=DEFAULT_BRANCH_ID,
        menu_item_id="item-biryani-01",
        record_date=date.today(),
        prepared_quantity=100,
        sold_quantity=82,
        remaining_quantity=18,
        wasted_quantity=18,
        waste_reason="over_production",
        notes="Dinner test service"
    )
    log_res = log_waste_entry(test_db, entry)
    assert log_res.waste_percentage == 18.0
    assert log_res.cost_wasted > 0
    assert log_res.corrective_action_recommended is not None
    
    # Check analytics aggregation
    analytics = get_waste_analytics(test_db, DEFAULT_BRANCH_ID)
    assert analytics.total_prepared > 0
    assert analytics.total_wasted > 0
    assert len(analytics.cause_breakdown) > 0
    assert any(c.reason == "over_production" for c in analytics.cause_breakdown)

def test_what_if_simulator(test_db):
    req = WhatIfSimulationRequest(
        branch_id=DEFAULT_BRANCH_ID,
        target_date=date.today(),
        weather_scenario="Heavy Rain",
        rainfall_override=30.0,
        temperature_override=20.0,
        is_holiday=True,
        is_festival=False,
        active_promotion=True,
        demand_shift_percentage=15.0
    )
    sim_res = run_what_if_simulation(test_db, req)
    assert sim_res.total_baseline_demand > 0
    assert sim_res.total_simulated_demand > 0
    assert len(sim_res.item_simulations) > 0
    assert "predictions represent what-if estimates" in sim_res.disclaimer.lower()

def test_operational_alert_engine(test_db):
    alerts = evaluate_and_generate_alerts(test_db, DEFAULT_BRANCH_ID)
    assert len(alerts) >= 1
    
    first_alert = alerts[0]
    ack = acknowledge_alert(test_db, first_alert.id, "acknowledged")
    assert ack.status == "acknowledged"

def test_donation_workflow_and_safety_gate(test_db):
    candidates = detect_surplus_candidates(test_db, DEFAULT_BRANCH_ID)
    assert isinstance(candidates, list)
    
    # Attempting to certify with failed visual check must raise ValueError
    with pytest.raises(ValueError):
        register_food_safe_donation(test_db, FoodSafetyCertificationRequest(
            branch_id=DEFAULT_BRANCH_ID,
            menu_item_id="item-biryani-01",
            surplus_quantity=10,
            certified_by="Chef Marcus",
            temperature_verified_celsius=65.0,
            visual_inspection_passed=False, # FAILS
            packaging_intact=True,
            recipient_ngo="City Harvest Food Bank"
        ))
        
    # Valid certification passes
    valid_cert = FoodSafetyCertificationRequest(
        branch_id=DEFAULT_BRANCH_ID,
        menu_item_id="item-biryani-01",
        surplus_quantity=12,
        certified_by="Head Chef Elena",
        temperature_verified_celsius=68.5,
        visual_inspection_passed=True,
        packaging_intact=True,
        recipient_ngo="City Harvest Community Food Bank"
    )
    donation = register_food_safe_donation(test_db, valid_cert)
    assert donation.food_safe_certified is True
    assert donation.impact_meals_saved == 12
    assert donation.carbon_avoided_kg > 0

def test_sustainability_metrics(test_db):
    sust = calculate_sustainability_metrics(test_db, DEFAULT_BRANCH_ID, days=30)
    assert sust.total_food_prepared_portions > 0
    assert sust.estimated_co2e_avoided_kg > 0
    assert sust.estimated_water_saved_liters > 0
    assert len(sust.environmental_factors) == 3
    assert "USDA & WRI" in sust.methodology_statement or "estimated" in sust.methodology_statement
