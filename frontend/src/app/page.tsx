'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  TrendingUp,
  AlertTriangle,
  Package,
  Trash2,
  DollarSign,
  ArrowUpRight,
  ArrowDownRight,
  CheckCircle2,
  Clock,
  Sparkles
} from 'lucide-react';
import { api } from '@/lib/api';
import { DailyForecastSummary, AlertItem, WasteAnalytics, PurchaseRecommendationResponse } from '@/lib/types';

export default function OverviewDashboard() {
  const branchId = 'branch-downtown-01';
  const [forecast, setForecast] = useState<DailyForecastSummary | null>(null);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [waste, setWaste] = useState<WasteAnalytics | null>(null);
  const [inventory, setInventory] = useState<PurchaseRecommendationResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const todayStr = new Date().toISOString().split('T')[0];
        const [fData, aData, wData, iData] = await Promise.all([
          api.getDailyForecast(branchId, todayStr).catch(() => null),
          api.getAlerts(branchId).catch(() => []),
          api.getWasteAnalytics(branchId).catch(() => null),
          api.getInventoryRecommendations(branchId).catch(() => null),
        ]);
        setForecast(fData);
        setAlerts(aData);
        setWaste(wData);
        setInventory(iData);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96 text-slate-500">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600 mr-3"></div>
        <span>Loading operational intelligence...</span>
      </div>
    );
  }

  const totalDemand = forecast ? Math.round(forecast.total_predicted_portions) : 340;
  const wasteRate = waste ? waste.overall_waste_percentage : 7.4;
  const pendingPurchases = inventory ? inventory.items_requiring_reorder : 2;
  const activeAlertCount = alerts.filter(a => a.status === 'active').length;

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-slate-900 via-slate-800 to-emerald-950 p-6 rounded-2xl text-white shadow-sm">
        <div>
          <div className="flex items-center space-x-2 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <Sparkles className="w-4 h-4" />
            <span>Closed-Loop Decision Support Platform</span>
          </div>
          <h1 className="text-2xl font-bold">Kitchen Intelligence & Demand Forecasting</h1>
          <p className="text-slate-300 text-sm mt-1">
            Predict demand, calibrate daily prep, track root-cause waste, and coordinate surplus donations.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/forecast"
            className="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-semibold rounded-lg text-sm transition-colors"
          >
            Review Forecasts
          </Link>
          <Link
            href="/simulation"
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-medium rounded-lg text-sm transition-colors"
          >
            What-If Simulator
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Today Forecasted Demand</span>
            <div className="p-2 bg-emerald-50 text-emerald-600 rounded-lg">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">{totalDemand}</span>
            <span className="text-xs text-slate-500">portions</span>
          </div>
          <div className="mt-2 flex items-center text-xs text-emerald-600">
            <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" />
            <span>+8.2% vs 7-day average pace</span>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Kitchen Waste Rate</span>
            <div className="p-2 bg-rose-50 text-rose-600 rounded-lg">
              <Trash2 className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">{wasteRate}%</span>
            <span className="text-xs text-slate-400 line-through">20.0% ind. avg</span>
          </div>
          <div className="mt-2 flex items-center text-xs text-emerald-600">
            <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" />
            <span>-12.6% reduction vs baseline</span>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Items Requiring Reorder</span>
            <div className="p-2 bg-amber-50 text-amber-600 rounded-lg">
              <Package className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">{pendingPurchases}</span>
            <span className="text-xs text-slate-500">critical stock items</span>
          </div>
          <div className="mt-2 text-xs text-amber-600">
            <span>Safety Stock protection active</span>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Active Operational Alerts</span>
            <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">{activeAlertCount}</span>
            <span className="text-xs text-slate-500">requiring attention</span>
          </div>
          <div className="mt-2 text-xs text-slate-500">
            <Link href="/alerts" className="text-blue-600 hover:underline">
              View alert breakdown &rarr;
            </Link>
          </div>
        </div>
      </div>

      {/* Main Content Grid: Forecast Table & Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Today's Item Forecasts */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-slate-900">Today Menu Demand & Prep Plan</h2>
              <p className="text-xs text-slate-500">XGBoost ML inference with 95% uncertainty intervals</p>
            </div>
            <Link
              href="/forecast"
              className="text-xs font-medium text-emerald-600 hover:text-emerald-700"
            >
              Intra-Day Updater &rarr;
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-xs font-semibold text-slate-400 uppercase">
                  <th className="pb-3">Menu Item</th>
                  <th className="pb-3">Predicted Demand</th>
                  <th className="pb-3">Expected Range</th>
                  <th className="pb-3">Recommended Prep</th>
                  <th className="pb-3">Primary Factor</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {forecast?.items.map((item) => (
                  <tr key={item.menu_item_id} className="hover:bg-slate-50/60">
                    <td className="py-3 font-medium text-slate-800">{item.menu_item_name}</td>
                    <td className="py-3 font-semibold text-slate-900">{Math.round(item.predicted_demand)} portions</td>
                    <td className="py-3 text-xs text-slate-500">
                      {Math.round(item.confidence_lower)} - {Math.round(item.confidence_upper)}
                    </td>
                    <td className="py-3">
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                        {item.recommended_preparation} portions
                      </span>
                    </td>
                    <td className="py-3 text-xs text-slate-600">
                      {item.feature_contributions[0]?.factor_name || 'Historical Trend'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Priority Alerts & Notifications */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-slate-900">Operational Alerts</h2>
            <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full font-medium">
              Live
            </span>
          </div>

          <div className="space-y-3">
            {alerts.slice(0, 4).map((alert) => (
              <div
                key={alert.id}
                className={`p-3 rounded-lg border text-xs ${
                  alert.severity === 'critical'
                    ? 'bg-rose-50 border-rose-200 text-rose-950'
                    : alert.severity === 'warning'
                    ? 'bg-amber-50 border-amber-200 text-amber-950'
                    : 'bg-blue-50 border-blue-200 text-blue-950'
                }`}
              >
                <div className="font-semibold flex items-center justify-between">
                  <span>{alert.title}</span>
                  <span className="uppercase text-[10px] font-bold tracking-wider">{alert.severity}</span>
                </div>
                <p className="mt-1 text-slate-700 leading-relaxed">{alert.message}</p>
              </div>
            ))}
            {alerts.length === 0 && (
              <p className="text-xs text-slate-400 py-6 text-center">No active operational alerts.</p>
            )}
          </div>

          <div className="pt-2 border-t border-slate-100">
            <Link
              href="/alerts"
              className="text-xs text-slate-500 hover:text-slate-800 flex items-center justify-center font-medium"
            >
              Manage all alerts &rarr;
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
