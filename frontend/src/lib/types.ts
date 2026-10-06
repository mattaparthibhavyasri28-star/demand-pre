export interface ExplainabilityFactor {
  factor_name: string;
  impact_percentage: number;
  description: string;
}

export interface ItemPrediction {
  branch_id: string;
  menu_item_id: string;
  menu_item_name: string;
  target_date: string;
  predicted_demand: number;
  confidence_lower: number;
  confidence_upper: number;
  recommended_preparation: number;
  model_name: string;
  model_version: string;
  feature_contributions: ExplainabilityFactor[];
}

export interface DailyForecastSummary {
  date: string;
  total_predicted_portions: number;
  items: ItemPrediction[];
}

export interface NearRealTimeUpdate {
  branch_id: string;
  menu_item_id: string;
  menu_item_name: string;
  target_date: string;
  current_hour: number;
  initial_daily_prediction: number;
  cumulative_sales_so_far: number;
  updated_predicted_total: number;
  remaining_predicted_sales: number;
  recommended_additional_prep: number;
  status_assessment: 'on_track' | 'surging_demand' | 'lagging_demand';
  explanation: string;
}

export interface IngredientRequirement {
  ingredient_id: string;
  ingredient_name: string;
  category: string;
  unit: string;
  unit_cost: number;
  current_stock: number;
  predicted_demand_consumption: number;
  safety_stock: number;
  reorder_point: number;
  net_deficit: number;
  recommended_purchase: number;
  estimated_purchase_cost: number;
  urgency: 'normal' | 'reorder_needed' | 'critical_stockout';
}

export interface PurchaseRecommendationResponse {
  branch_id: string;
  planning_date: string;
  total_estimated_purchase_cost: number;
  items_requiring_reorder: number;
  recommendations: IngredientRequirement[];
  methodology_notes: string;
}

export interface WasteCauseBreakdown {
  reason: string;
  display_name: string;
  quantity: number;
  cost: number;
  percentage_of_total_waste: number;
}

export interface ActionableRecommendation {
  menu_item_id: string;
  menu_item_name: string;
  issue_detected: string;
  recommended_action: string;
  expected_savings_portions: number;
  expected_cost_reduction: number;
}

export interface WasteRecord {
  id: string;
  branch_id: string;
  menu_item_id: string;
  menu_item_name: string;
  record_date: string;
  prepared_quantity: number;
  sold_quantity: number;
  remaining_quantity: number;
  wasted_quantity: number;
  waste_percentage: number;
  waste_reason: string;
  cost_wasted: number;
  notes?: string;
  corrective_action_recommended?: string;
  created_at: string;
}

export interface WasteAnalytics {
  branch_id: string;
  start_date: string;
  end_date: string;
  total_prepared: number;
  total_sold: number;
  total_wasted: number;
  overall_waste_percentage: number;
  total_cost_wasted: number;
  cause_breakdown: WasteCauseBreakdown[];
  actionable_recommendations: ActionableRecommendation[];
  recent_logs: WasteRecord[];
}

export interface SimulatedItemResult {
  menu_item_id: string;
  menu_item_name: string;
  baseline_demand: number;
  simulated_demand: number;
  demand_change_percentage: number;
  recommended_preparation: number;
  predicted_waste_risk_portions: number;
  risk_level: 'low' | 'moderate' | 'high';
}

export interface WhatIfSimulationResponse {
  branch_id: string;
  target_date: string;
  scenario_description: string;
  total_baseline_demand: number;
  total_simulated_demand: number;
  net_demand_change_pct: number;
  total_estimated_waste_risk: number;
  key_drivers: string[];
  item_simulations: SimulatedItemResult[];
  disclaimer: string;
}

export interface AlertItem {
  id: string;
  branch_id: string;
  alert_type: string;
  severity: 'info' | 'warning' | 'critical';
  title: string;
  message: string;
  metadata?: Record<string, any>;
  status: 'active' | 'acknowledged' | 'resolved';
  created_at: string;
}

export interface SurplusCandidate {
  menu_item_id: string;
  menu_item_name: string;
  surplus_quantity: number;
  unit: string;
  safe_to_donate: boolean;
  recommended_discount_portion: number;
  recommended_donation_portion: number;
  estimated_shelf_life_remaining_hours: number;
}

export interface DonationRecord {
  id: string;
  branch_id: string;
  menu_item_id: string;
  menu_item_name: string;
  surplus_quantity: number;
  unit: string;
  food_safe_certified: boolean;
  certified_by?: string;
  recipient_ngo?: string;
  pickup_status: string;
  impact_meals_saved: number;
  carbon_avoided_kg: number;
  created_at: string;
  disclaimer: string;
}

export interface EnvironmentalFactor {
  category: string;
  amount_saved: number;
  unit: string;
  methodology: string;
}

export interface SustainabilitySummary {
  branch_id: string;
  reporting_period: string;
  total_food_prepared_portions: number;
  total_food_sold_portions: number;
  total_food_wasted_portions: number;
  waste_percentage: number;
  estimated_meals_diverted_from_landfill: number;
  estimated_cost_saved_usd: number;
  meals_donated_to_ngos: number;
  estimated_co2e_avoided_kg: number;
  estimated_water_saved_liters: number;
  trend_waste_reduction_pct: number;
  environmental_factors: EnvironmentalFactor[];
  methodology_statement: string;
}

export interface BranchInfo {
  id: string;
  name: string;
  restaurant_name: string;
  city: string;
  address: string;
}
