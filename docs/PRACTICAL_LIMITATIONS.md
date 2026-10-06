# Practical Limitations & Engineering Transparency

This document records honest practical limitations and boundaries of the current implementation:

1. **Synthetic Training Dataset Limitation**:
   - The primary benchmark dataset was synthetically generated across 365 days of multi-item restaurant operations. While it incorporates realistic diurnal patterns, seasonality, weather dampening, and holiday shocks, real restaurant POS data contains idiosyncrasies, customer walk-in volatility, cancellations, and kitchen logging variances.
   - The system is architected to seamlessly ingest real CSV/POS streams without requiring code modifications.

2. **No Guaranteed 100% Elimination of Food Waste**:
   - The platform is a **decision-support tool**; it does not claim to completely eliminate food waste. Random customer demand surges and dips will always occur in hospitality operations.

3. **Food Safety Certification Cannot Be Automated**:
   - The software assists with surplus detection and NGO dispatch coordination, but **cannot and must not independently certify microbiological food safety**. Final acceptance and sign-off remain strictly with certified human kitchen and partner personnel.

4. **Environmental Impact Estimates**:
   - Metrics such as CO2e avoided and water preserved are **model-estimated** using published Life Cycle Assessment (LCA) factors (USDA, WRI, FAO), not direct physical sensors or real-time carbon meters.

5. **Weather Correlation Sensitivity**:
   - Weather affects different items differently (e.g. rain dampens walk-ins for dine-in restaurants while boosting delivery orders for pizza/comfort food). Weather features improve accuracy only where causal historical correlations exist.

6. **Demand Forecasts Are Probabilistic**:
   - Demand predictions represent statistical estimates, which is why the platform explicitly surfaces 95% confidence intervals and what-if simulation disclaimers.
