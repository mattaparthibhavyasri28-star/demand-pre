import pytest
from datetime import date
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.seed_data import DEFAULT_BRANCH_ID

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_health_check_endpoint(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"

def test_branches_endpoint(client):
    res = client.get("/api/v1/branches")
    assert res.status_code == 200
    branches = res.json()
    assert len(branches) > 0
    assert any(b["id"] == DEFAULT_BRANCH_ID for b in branches)

def test_daily_forecast_endpoint(client):
    res = client.get(f"/api/v1/demand/daily-forecast?branch_id={DEFAULT_BRANCH_ID}&target_date=2026-10-10")
    assert res.status_code == 200
    data = res.json()
    assert "total_predicted_portions" in data
    assert len(data["items"]) == 6
    assert data["items"][0]["confidence_lower"] <= data["items"][0]["confidence_upper"]

def test_inventory_recommendations_endpoint(client):
    res = client.get(f"/api/v1/inventory/recommendations?branch_id={DEFAULT_BRANCH_ID}")
    assert res.status_code == 200
    data = res.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0

def test_waste_analytics_endpoint(client):
    res = client.get(f"/api/v1/waste/analytics?branch_id={DEFAULT_BRANCH_ID}")
    assert res.status_code == 200
    data = res.json()
    assert "cause_breakdown" in data
    assert "actionable_recommendations" in data

def test_what_if_simulation_endpoint(client):
    payload = {
        "branch_id": DEFAULT_BRANCH_ID,
        "target_date": "2026-10-12",
        "weather_scenario": "Heavy Rain",
        "is_holiday": True,
        "demand_shift_percentage": 10.0
    }
    res = client.post("/api/v1/simulation/what-if", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["net_demand_change_pct"] != 0
    assert len(data["item_simulations"]) > 0

def test_alerts_endpoint(client):
    res = client.get(f"/api/v1/alerts?branch_id={DEFAULT_BRANCH_ID}")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_sustainability_summary_endpoint(client):
    res = client.get(f"/api/v1/sustainability/summary?branch_id={DEFAULT_BRANCH_ID}&days=30")
    assert res.status_code == 200
    data = res.json()
    assert data["estimated_co2e_avoided_kg"] > 0
    assert data["estimated_water_saved_liters"] > 0

def test_copilot_endpoints(client):
    # Status
    res_status = client.get("/api/v1/copilot/status")
    assert res_status.status_code == 200
    assert "provider" in res_status.json()

    # Briefing
    res_brief = client.get(f"/api/v1/copilot/daily-briefing?branch_id={DEFAULT_BRANCH_ID}")
    assert res_brief.status_code == 200
    assert "briefing_text" in res_brief.json()

    # Surplus repurpose
    res_rep = client.post("/api/v1/copilot/surplus-repurpose", json={
        "menu_item_name": "Chicken Biryani",
        "surplus_quantity": 12
    })
    assert res_rep.status_code == 200
    assert "repurposing_plan" in res_rep.json()

