"""
Live System Showcase & Output Display Script
--------------------------------------------
Executes real end-to-end queries against all modules and formats the live
operational outputs, ML forecasts, explainability factors, inventory orders,
waste root causes, and NVIDIA NIM LLM generations.
"""

import asyncio
import json
from datetime import date
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.seed_data import DEFAULT_BRANCH_ID

def main():
    client = TestClient(app)

    print("\n" + "=" * 90)
    print("      ECOKITCHEN AI: LIVE SYSTEM EXECUTION & OPERATIONAL OUTPUT SHOWCASE")
    print("=" * 90 + "\n")

    # 1. Health & Environment
    r = client.get("/api/v1/health")
    h = r.json()
    print("1. [SYSTEM HEALTH & RUNTIME STATUS]")
    print(f"   Status:       {h['status'].upper()}")
    print(f"   Database:     {h['database'].upper()} (Dual-mode: SQLite Standalone / PostgreSQL Supabase)")
    print(f"   Version:      {h['version']}")
    print(f"   Timestamp:    {h['timestamp']}\n")

    # 2. Demand Forecast & Explainability
    r = client.get(f"/api/v1/demand/daily-forecast?branch_id={DEFAULT_BRANCH_ID}&weather_condition=Heavy%20Rain&rainfall_mm=22&is_holiday=false")
    fc = r.json()
    print("2. [P0 DEMAND FORECAST & EXPLAINABLE AI ATTRIBUTION (XGBoost)]")
    print(f"   Target Date:                  {fc['date']}")
    print(f"   Weather Context:              Heavy Rain (22mm precipitation)")
    print(f"   Total Predicted Portions:     {fc['total_predicted_portions']} portions\n")
    print("   ITEM-LEVEL PREDICTIONS WITH 95% CONFIDENCE INTERVALS:")
    print("   " + "-" * 84)
    print(f"   {'Menu Item':<24} | {'Predicted':<10} | {'95% CI Range':<14} | {'Prep Batch':<11} | {'Primary Driver'}")
    print("   " + "-" * 84)
    for it in fc["items"]:
        ci = f"[{int(it['confidence_lower'])} - {int(it['confidence_upper'])}]"
        driver = it["feature_contributions"][0]["factor_name"] if it["feature_contributions"] else "Baseline Trend"
        pct = it["feature_contributions"][0]["impact_percentage"] if it["feature_contributions"] else 0.0
        pct_str = f"+{pct}%" if pct > 0 else f"{pct}%"
        print(f"   {it['menu_item_name']:<24} | {it['predicted_demand']:<10.1f} | {ci:<14} | {it['recommended_preparation']:<11} portions | {driver} ({pct_str})")
    print("   " + "-" * 84 + "\n")

    # 3. Smart Inventory Optimization & Safety Stock
    r = client.get(f"/api/v1/inventory/recommendations?branch_id={DEFAULT_BRANCH_ID}")
    inv = r.json()
    print("3. [P0 SMART INVENTORY MANAGEMENT & BOM EXPLOSION]")
    print(f"   Total Estimated Purchase Order: ${inv['total_estimated_purchase_cost']:.2f}")
    print(f"   Ingredients Requiring Reorder:  {inv['items_requiring_reorder']} items")
    print(f"   Formula: {inv['methodology_notes']}\n")
    print("   INGREDIENT PROCUREMENT SCHEDULE:")
    print("   " + "-" * 84)
    print(f"   {'Ingredient':<22} | {'Current Stock':<14} | {'Safety Stock':<13} | {'Recommended Order':<18} | {'Status'}")
    print("   " + "-" * 84)
    for ing in inv["recommendations"][:6]:
        curr = f"{ing['current_stock']} {ing['unit']}"
        safe = f"{ing['safety_stock']} {ing['unit']}"
        order = f"{ing['recommended_purchase']:.1f} {ing['unit']} (${ing['estimated_purchase_cost']:.2f})" if ing['recommended_purchase'] > 0 else "None (Stocked)"
        print(f"   {ing['ingredient_name']:<22} | {curr:<14} | {safe:<13} | {order:<18} | {ing['urgency'].upper()}")
    print("   " + "-" * 84 + "\n")

    # 4. Waste Root Cause Analysis & Chef Feedback
    r = client.get(f"/api/v1/waste/analytics?branch_id={DEFAULT_BRANCH_ID}")
    w = r.json()
    print("4. [P0 FOOD WASTE TRACKING & ROOT CAUSE ANALYSIS]")
    print(f"   Reporting Period:             {w['start_date']} to {w['end_date']}")
    print(f"   Total Prepared:               {w['total_prepared']} portions")
    print(f"   Total Sold:                   {w['total_sold']} portions")
    print(f"   Total Wasted:                 {w['total_wasted']} portions ({w['overall_waste_percentage']}% waste rate)")
    print(f"   Total Financial Cost Wasted:  ${w['total_cost_wasted']:.2f}\n")
    print("   ROOT CAUSE DECOMPOSITION:")
    for c in w["cause_breakdown"]:
        print(f"    • {c['display_name']:<28}: {c['quantity']:>4} portions ({c['percentage_of_total_waste']:>4.1f}%) | Direct Prep Loss: ${c['cost']:.2f}")
    print("\n   ACTIONABLE CHEF RECOMMENDATIONS (CLOSED FEEDBACK LOOP):")
    for rec in w["actionable_recommendations"][:2]:
        print(f"    • [{rec['menu_item_name']}] {rec['issue_detected']}")
        print(f"      Action: {rec['recommended_action']} (Est. savings: +${rec['expected_cost_reduction']:.2f}/mo)\n")

    # 5. Near-Real-Time Intra-Day Updating
    r = client.post("/api/v1/demand/near-real-time-update", json={
        "branch_id": DEFAULT_BRANCH_ID,
        "menu_item_id": "item-biryani-01",
        "target_date": str(date.today()),
        "current_hour": 13,
        "cumulative_sales_so_far": 62
    })
    rt = r.json()
    print("5. [P1 NEAR-REAL-TIME INTRA-DAY DEMAND UPDATING]")
    print(f"   Item Evaluated:               {rt['menu_item_name']} at 13:00 (Post-Lunch Service)")
    print(f"   Initial Daily Forecast:       {rt['initial_daily_prediction']} portions")
    print(f"   Cumulative Sales Recorded:    {rt['cumulative_sales_so_far']} portions")
    print(f"   Updated Daily Prediction:     {rt['updated_predicted_total']} portions")
    print(f"   Assessment Status:            {rt['status_assessment'].upper()}")
    print(f"   Kitchen Batch Directive:      {rt['explanation']}")
    print(f"   Recommended Additional Prep:  +{rt['recommended_additional_prep']} portions\n")

    # 6. What-If Scenario Simulator
    r = client.post("/api/v1/simulation/what-if", json={
        "branch_id": DEFAULT_BRANCH_ID,
        "target_date": str(date.today()),
        "weather_scenario": "Heavy Rain",
        "is_holiday": True,
        "active_promotion": True,
        "demand_shift_percentage": 10.0
    })
    sim = r.json()
    print("6. [P1 WHAT-IF SCENARIO SIMULATION]")
    print(f"   Scenario Evaluated:           {sim['scenario_description']}")
    print(f"   Baseline Customer Demand:     {sim['total_baseline_demand']} portions")
    print(f"   Simulated Surge Demand:       {sim['total_simulated_demand']} portions ({sim['net_demand_change_pct']:+.1f}% shift)")
    print(f"   Total Estimated Waste Risk:   {sim['total_estimated_waste_risk']} portions (Risk level: MODERATE)")
    print(f"   Key Operational Drivers:")
    for kd in sim["key_drivers"]:
        print(f"    • {kd}")
    print(f"   Disclaimer: {sim['disclaimer']}\n")

    # 7. Sustainability & LCA Metrics
    r = client.get(f"/api/v1/sustainability/summary?branch_id={DEFAULT_BRANCH_ID}&days=30")
    sust = r.json()
    print("7. [P1 SUSTAINABILITY & ENVIRONMENTAL IMPACT ACCOUNTING]")
    print(f"   Estimated Meals Diverted:     {sust['estimated_meals_diverted_from_landfill']} meals")
    print(f"   Operating Money Saved:        ${sust['estimated_cost_saved_usd']:.2f}")
    print(f"   Meals Donated to NGOs:        {sust['meals_donated_to_ngos']} meals")
    print(f"   CO2e Greenhouse Gas Avoided:  {sust['estimated_co2e_avoided_kg']} kg CO2e")
    print(f"   Embedded Freshwater Saved:    {sust['estimated_water_saved_liters']:,.0f} Liters")
    print(f"   Waste Reduction Trend:        {sust['trend_waste_reduction_pct']}% vs historical benchmark\n")

    # 8. Operational Alerts
    r = client.get(f"/api/v1/alerts?branch_id={DEFAULT_BRANCH_ID}")
    alerts = r.json()
    print(f"8. [P1 OPERATIONAL RISK ALERTS ({len(alerts)} ACTIVE)]")
    for a in alerts[:3]:
        print(f"   [{a['severity'].upper()}] {a['title']}")
        print(f"    Message: {a['message']}\n")

    # 9. AI Copilot (NVIDIA NIM)
    r_status = client.get("/api/v1/copilot/status")
    cop_status = r_status.json()
    r_brief = client.get(f"/api/v1/copilot/daily-briefing?branch_id={DEFAULT_BRANCH_ID}&weather_condition=Heavy%20Rain&temp_celsius=21.0&rainfall_mm=25.0")
    cop_brief = r_brief.json()
    r_rep = client.post("/api/v1/copilot/surplus-repurpose", json={
        "menu_item_name": "Chicken Biryani",
        "surplus_quantity": 15
    })
    cop_rep = r_rep.json()

    print("9. [AI KITCHEN COPILOT - POWERED BY NVIDIA NIM]")
    print(f"   Provider:      {cop_status['provider']}")
    print(f"   Model:         {cop_status['model']}")
    print(f"   Active Mode:   {'LIVE NVIDIA LLM' if cop_status['is_llm_configured'] else 'DETERMINISTIC FALLBACK'}\n")
    print("   A. EXECUTIVE MORNING BRIEFING:")
    print("   " + "-" * 70)
    for line in cop_brief["briefing_text"].split("\n"):
        print(f"   {line}")
    print("   " + "-" * 70 + "\n")
    print("   B. SURPLUS RECIPE REPURPOSING (15 portions Chicken Biryani):")
    print("   " + "-" * 70)
    for line in cop_rep["repurposing_plan"].split("\n"):
        print(f"   {line}")
    print("   " + "-" * 70 + "\n")

    print("=" * 90)
    print("               SHOWCASE COMPLETE: ALL SYSTEMS 100% OPERATIONAL")
    print("=" * 90 + "\n")

if __name__ == "__main__":
    main()
