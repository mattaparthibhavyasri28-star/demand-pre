'use client';

import React, { useEffect, useState } from 'react';
import {
  PackageSearch,
  AlertOctagon,
  CheckCircle,
  Clock,
  DollarSign,
  Calculator,
  ShieldCheck,
  TrendingUp
} from 'lucide-react';
import { api } from '@/lib/api';
import { PurchaseRecommendationResponse } from '@/lib/types';

export default function SmartInventoryPage() {
  const branchId = 'branch-downtown-01';
  const [data, setData] = useState<PurchaseRecommendationResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadInventory() {
      try {
        const res = await api.getInventoryRecommendations(branchId);
        setData(res);
      } finally {
        setLoading(false);
      }
    }
    loadInventory();
  }, []);

  if (loading) {
    return <div className="text-center py-12 text-slate-500">Calculating ingredient consumption & safety stock...</div>;
  }

  const recommendations = data?.recommendations || [];
  const totalCost = data?.total_estimated_purchase_cost || 0;
  const reorderCount = data?.items_requiring_reorder || 0;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Smart Inventory Management</h1>
          <p className="text-sm text-slate-500 mt-1">
            Ingredient demand exploded from forecasted menu portions with dynamic safety stock protection.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="bg-white border border-slate-200 px-4 py-2 rounded-xl text-right">
            <span className="text-[11px] font-semibold text-slate-400 block uppercase">Estimated Purchase Order</span>
            <span className="text-lg font-bold text-slate-900">${totalCost.toFixed(2)}</span>
          </div>
        </div>
      </div>

      {/* Methodology Highlight Alert */}
      <div className="bg-emerald-50 border border-emerald-200 p-4 rounded-xl text-xs text-emerald-950 flex items-start space-x-3">
        <Calculator className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-emerald-900 block">Documented Safety Stock Formula</span>
          <p className="mt-0.5 text-emerald-800 leading-relaxed">
            {data?.methodology_notes ||
              'Safety Stock = Z × √(Lead Time Days) × σ(Daily Demand), with Z = 1.65 (95% service level) over 2.0 days supplier lead time.'}
          </p>
        </div>
      </div>

      {/* Reorder Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <span className="text-xs text-slate-500 font-medium">Critical Stock-Out Items</span>
          <div className="mt-2 text-2xl font-bold text-rose-600">
            {recommendations.filter((r) => r.urgency === 'critical_stockout').length}
          </div>
          <p className="text-xs text-slate-400 mt-1">Current stock below safety threshold</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <span className="text-xs text-slate-500 font-medium">Reorder Point Triggered</span>
          <div className="mt-2 text-2xl font-bold text-amber-600">{reorderCount}</div>
          <p className="text-xs text-slate-400 mt-1">Order recommended within 48 hours</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <span className="text-xs text-slate-500 font-medium">Stock Sufficient Items</span>
          <div className="mt-2 text-2xl font-bold text-emerald-600">
            {recommendations.filter((r) => r.urgency === 'normal').length}
          </div>
          <p className="text-xs text-slate-400 mt-1">Covers forecasted consumption</p>
        </div>
      </div>

      {/* Ingredient BOM & Purchase Recommendation Table */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-bold text-slate-900">Procurement & Stock Status</h2>
          <span className="text-xs text-slate-400">Planning Horizon: Tomorrow</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-100 text-xs font-semibold text-slate-400 uppercase">
                <th className="pb-3">Ingredient</th>
                <th className="pb-3">Category</th>
                <th className="pb-3">Current Stock</th>
                <th className="pb-3">Predicted Usage</th>
                <th className="pb-3">Safety Stock</th>
                <th className="pb-3">Net Deficit</th>
                <th className="pb-3">Recommended Purchase</th>
                <th className="pb-3">Est Cost</th>
                <th className="pb-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {recommendations.map((ing) => (
                <tr key={ing.ingredient_id} className="hover:bg-slate-50/60">
                  <td className="py-3 font-semibold text-slate-900">{ing.ingredient_name}</td>
                  <td className="py-3 text-xs text-slate-500">{ing.category}</td>
                  <td className="py-3 text-slate-800">
                    {ing.current_stock.toFixed(1)} {ing.unit}
                  </td>
                  <td className="py-3 text-slate-700">
                    {ing.predicted_demand_consumption.toFixed(1)} {ing.unit}
                  </td>
                  <td className="py-3 text-slate-500 text-xs">
                    {ing.safety_stock.toFixed(1)} {ing.unit}
                  </td>
                  <td className="py-3 text-xs font-medium text-slate-600">
                    {ing.net_deficit > 0 ? `+${ing.net_deficit.toFixed(1)}` : '0.0'} {ing.unit}
                  </td>
                  <td className="py-3 font-bold text-slate-900">
                    {ing.recommended_purchase > 0 ? (
                      <span className="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">
                        {ing.recommended_purchase.toFixed(1)} {ing.unit}
                      </span>
                    ) : (
                      <span className="text-slate-400 font-normal">None</span>
                    )}
                  </td>
                  <td className="py-3 text-xs text-slate-700 font-medium">
                    ${ing.estimated_purchase_cost.toFixed(2)}
                  </td>
                  <td className="py-3">
                    {ing.urgency === 'critical_stockout' ? (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold bg-rose-50 text-rose-700 border border-rose-200">
                        Critical Deficit
                      </span>
                    ) : ing.urgency === 'reorder_needed' ? (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-amber-50 text-amber-700 border border-amber-200">
                        Reorder Needed
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                        Optimal
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
