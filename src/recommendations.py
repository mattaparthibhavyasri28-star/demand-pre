"""Transparent preparation and estimated-waste calculations."""

from __future__ import annotations

import math


def preparation_recommendation(predicted_demand: float, prepared_quantity: int,
                               tolerance: float = 0.10) -> dict[str, float | str]:
    """Compare current planned prep to forecast; use a simple 10% tolerance."""
    if predicted_demand < 0 or prepared_quantity < 0:
        raise ValueError("Demand and prepared quantity cannot be negative.")
    demand = max(0, float(predicted_demand))
    prepared = int(prepared_quantity)
    excess = max(0.0, prepared - demand)
    waste_pct = (excess / prepared * 100) if prepared else 0.0
    difference = prepared - demand
    if demand == 0 and prepared > 0:
        action = "Reduce preparation substantially; forecast demand is zero."
    elif difference > max(1.0, demand * tolerance):
        action = f"Reduce preparation by about {math.ceil(difference)} portions to align with forecast demand."
    elif difference < -max(1.0, demand * tolerance):
        action = f"Increase preparation by about {math.ceil(-difference)} portions to cover forecast demand."
    else:
        action = "Maintain the current preparation quantity; it is close to forecast demand."
    return {
        "excess_food": round(excess, 1),
        "estimated_wastage_percentage": round(waste_pct, 2),
        "recommended_quantity": int(math.ceil(demand)),
        "recommendation": action,
        "explanation": f"Compared {prepared} planned portions with {demand:.1f} forecast portions; excess is max(0, planned minus forecast).",
    }
