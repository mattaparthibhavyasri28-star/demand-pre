# Machine Learning Methodology & Empirical Validation

## 1. Objective
Forecast item-level daily portion demand to balance customer availability and minimize over-production kitchen waste.

## 2. Model Progression & Comparative Benchmarking

Four regression model architectures were fitted and evaluated on a strictly chronological holdout split (last 20% of consecutive dates; 438 test samples) to prevent temporal data leakage:

| Model Architecture | MAE (portions) | RMSE (portions) | MAPE (%) | R² Score | Selection Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Linear Regression (Baseline)** | 7.622 | 10.408 | 11.57% | 0.8534 | Baseline comparison |
| **Random Forest Regressor** | 5.507 | 8.012 | 7.79% | 0.9131 | Strong tree ensemble |
| **Gradient Boosting Regressor** | 5.246 | 7.109 | 7.59% | 0.9316 | High accuracy |
| **XGBoost Regressor (Selected)** | **5.163** | **7.045** | **7.49%** | **0.9328** | **Production Winner** |

### Empirical Validation Findings:
- XGBoost achieved the lowest Mean Absolute Error (5.16 portions) and highest explained variance (R² = 0.9328).
- Tree ensembles outperformed linear regression by ~32% on MAE, successfully capturing non-linear weather shock interactions and holiday surges.

## 3. Feature Pipeline & Importance Weights

The feature pipeline extracts 17 continuous, cyclical, and categorical signals:

```text
Feature Column          Relative Importance    Description
──────────────────────────────────────────────────────────────────────────
sales_lag_7             41.93%                 Sales volume same day prior week
sales_rolling_avg_7     16.78%                 7-day moving run-rate
day_of_week              8.67%                 Diurnal weekly demand cycles
promotion_active         7.12%                 Marketing discount impact
item_code                6.96%                 Menu item catalog embedding
festival_flag            5.47%                 Calendar festival event boost
holiday_flag             5.37%                 Public holiday leisure surge
rainfall_mm              1.94%                 Precipitation volume dampening/boost
weather_temp             1.55%                 Temperature preference shifts
unit_price               1.03%                 Price elasticity indicator
sales_lag_1              0.94%                 Previous day sales pace
sin_day_of_year          0.44%                 Annual seasonal solar cycle
cos_day_of_year          0.70%                 Annual seasonal solar cycle
sales_rolling_std_7      0.60%                 Demand volatility index
```

## 4. Confidence / Uncertainty Intervals

For every predicted value $\hat{y}$, the system constructs a 95% confidence interval derived from model standard error:

$$\text{Confidence Interval} = \hat{y} \pm 1.96 \cdot \sigma_{\text{residual}}$$

Example:
```text
Chicken Biryani
Predicted demand: 82 portions
Expected range (95% CI): 74 – 91 portions
Recommended kitchen prep: 82 portions
```

## 5. Explainable AI (XAI) Factor Decomposition

The system computes clear factor attributions explaining why demand shifted relative to the baseline:
- Weekend Surge: $+15\%$ to $+20\%$
- Festival / Holiday: $+14\%$ to $+25\%$
- Active Promotion: $+18.5\%$
- Heavy Rain: $-6.5\%$ (dine-in items) / $+8\%$ (delivery items)
- Hot Weather: $+12\%$ (chilled salads)

## 6. Closed-Loop Model Feedback Loop

When end-of-day sales are recorded, the system computes:
$$\text{Signed Error} = \text{Predicted Demand} - \text{Actual Sales}$$

If an item experiences systematic over-prediction ($\text{Mean Error} > 6.0$ portions over 7 days), the feedback loop automatically scales down the preparation multiplier ($\times 0.92$) to guard against repetitive kitchen over-preparation waste.
