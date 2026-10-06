'use client';

import React, { useState, useEffect } from 'react';
import {
  Trash2,
  PieChart,
  Lightbulb,
  DollarSign,
  AlertTriangle,
  PlusCircle,
  CheckCircle2,
  Filter
} from 'lucide-react';
import { api } from '@/lib/api';
import { WasteAnalytics } from '@/lib/types';

export default function WasteAnalyticsPage() {
  const branchId = 'branch-downtown-01';
  const [analytics, setAnalytics] = useState<WasteAnalytics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Form State for logging waste
  const [showLogModal, setShowLogModal] = useState<boolean>(false);
  const [formItemId, setFormItemId] = useState<string>('item-biryani-01');
  const [formPrepared, setFormPrepared] = useState<number>(90);
  const [formSold, setFormSold] = useState<number>(75);
  const [formReason, setFormReason] = useState<string>('over_production');
  const [formNotes, setFormNotes] = useState<string>('');
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [formSuccess, setFormSuccess] = useState<string>('');

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await api.getWasteAnalytics(branchId);
      setAnalytics(res);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleLogSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    const wasted = Math.max(0, formPrepared - formSold);
    try {
      await api.logWaste({
        branch_id: branchId,
        menu_item_id: formItemId,
        record_date: new Date().toISOString().split('T')[0],
        prepared_quantity: formPrepared,
        sold_quantity: formSold,
        remaining_quantity: wasted,
        wasted_quantity: wasted,
        waste_reason: formReason,
        notes: formNotes
      });
      setFormSuccess('Waste entry recorded. Closed-loop ML feedback loop updated.');
      setTimeout(() => {
        setFormSuccess('');
        setShowLogModal(false);
        loadData();
      }, 1500);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="text-center py-12 text-slate-500">Loading food waste tracking & causal intelligence...</div>;
  }

  const breakdown = analytics?.cause_breakdown || [];
  const recommendations = analytics?.actionable_recommendations || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Food Waste Tracking & Root Cause Analysis</h1>
          <p className="text-sm text-slate-500 mt-1">
            Granular causal attribution to eliminate unnecessary over-preparation and ingredient expiry.
          </p>
        </div>
        <button
          onClick={() => setShowLogModal(true)}
          className="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold px-4 py-2 rounded-xl text-sm transition-colors flex items-center space-x-2 shadow-xs"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Log Kitchen Shift Waste</span>
        </button>
      </div>

      {/* Top Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <span className="text-xs text-slate-500 font-medium">Total Food Prepared</span>
          <div className="mt-2 text-2xl font-bold text-slate-900">{analytics?.total_prepared} portions</div>
          <span className="text-xs text-slate-400">Past 30 days</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <span className="text-xs text-slate-500 font-medium">Total Food Sold</span>
          <div className="mt-2 text-2xl font-bold text-emerald-600">{analytics?.total_sold} portions</div>
          <span className="text-xs text-slate-400">Customer fulfillment</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <span className="text-xs text-slate-500 font-medium">Total Food Wasted</span>
          <div className="mt-2 text-2xl font-bold text-rose-600">{analytics?.total_wasted} portions</div>
          <span className="text-xs text-rose-500 font-medium">{analytics?.overall_waste_percentage}% rate</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <span className="text-xs text-slate-500 font-medium">Financial Cost of Waste</span>
          <div className="mt-2 text-2xl font-bold text-slate-900">${analytics?.total_cost_wasted.toFixed(2)}</div>
          <span className="text-xs text-slate-400">Direct ingredient prep loss</span>
        </div>
      </div>

      {/* Root Cause Breakdown & Actionable Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Root Cause Attribution */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
          <h2 className="text-base font-bold text-slate-900 mb-1">Waste Cause Decomposition</h2>
          <p className="text-xs text-slate-500 mb-4">Empirical attribution across 30 days of kitchen service</p>

          <div className="space-y-4">
            {breakdown.map((item) => (
              <div key={item.reason} className="space-y-1.5">
                <div className="flex items-center justify-between text-xs font-semibold">
                  <span className="text-slate-800">{item.display_name}</span>
                  <span className="text-slate-500">
                    {item.quantity} portions (${item.cost.toFixed(2)}) — {item.percentage_of_total_waste}%
                  </span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                  <div
                    className={`h-2.5 rounded-full ${
                      item.reason === 'over_production'
                        ? 'bg-rose-500'
                        : item.reason === 'expired_shelf_life'
                        ? 'bg-amber-500'
                        : item.reason === 'preparation_error'
                        ? 'bg-blue-500'
                        : 'bg-slate-400'
                    }`}
                    style={{ width: `${Math.min(100, item.percentage_of_total_waste)}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Actionable Chef Recommendations */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
          <div className="flex items-center space-x-2 mb-1">
            <Lightbulb className="w-4 h-4 text-amber-500" />
            <h2 className="text-base font-bold text-slate-900">Actionable Feedback Loop Recommendations</h2>
          </div>
          <p className="text-xs text-slate-500 mb-4">Automated corrective intelligence fed back into future prep</p>

          <div className="space-y-3">
            {recommendations.map((rec) => (
              <div key={rec.menu_item_id} className="p-3.5 rounded-xl border border-slate-200 bg-slate-50 text-xs">
                <div className="flex items-center justify-between font-bold text-slate-900 mb-1">
                  <span>{rec.menu_item_name}</span>
                  <span className="text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded text-[10px]">
                    Est Save: +${rec.expected_cost_reduction.toFixed(0)}/mo
                  </span>
                </div>
                <p className="text-slate-600 mb-1.5 leading-snug">
                  <strong>Issue:</strong> {rec.issue_detected}
                </p>
                <p className="text-emerald-800 font-medium bg-emerald-50 p-2 rounded-lg border border-emerald-200/60">
                  <strong>Action:</strong> {rec.recommended_action}
                </p>
              </div>
            ))}
            {recommendations.length === 0 && (
              <p className="text-xs text-slate-400 py-6 text-center">
                Preparation batches currently aligned with customer run rates.
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Modal for Logging Shift Waste */}
      {showLogModal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-200">
            <h3 className="text-lg font-bold text-slate-900">Log Kitchen Shift Waste</h3>
            <p className="text-xs text-slate-500 mt-1">
              Feeds empirical waste data directly back into model calibration.
            </p>

            <form onSubmit={handleLogSubmit} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Menu Item</label>
                <select
                  value={formItemId}
                  onChange={(e) => setFormItemId(e.target.value)}
                  className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2 text-slate-800"
                >
                  <option value="item-biryani-01">Chicken Biryani</option>
                  <option value="item-paneer-02">Paneer Butter Masala</option>
                  <option value="item-friedrice-03">Veg Fried Rice</option>
                  <option value="item-salmon-04">Grilled Salmon</option>
                  <option value="item-pizza-05">Margherita Pizza</option>
                  <option value="item-salad-06">Caesar Salad</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Prepared Portions</label>
                  <input
                    type="number"
                    min="1"
                    value={formPrepared}
                    onChange={(e) => setFormPrepared(parseInt(e.target.value) || 0)}
                    className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2 text-slate-800"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Sold Portions</label>
                  <input
                    type="number"
                    min="0"
                    value={formSold}
                    onChange={(e) => setFormSold(parseInt(e.target.value) || 0)}
                    className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2 text-slate-800"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Primary Waste Reason</label>
                <select
                  value={formReason}
                  onChange={(e) => setFormReason(e.target.value)}
                  className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2 text-slate-800"
                >
                  <option value="over_production">Over-Production (Leftover at close)</option>
                  <option value="expired_shelf_life">Expired Shelf Life / Holding Temperature</option>
                  <option value="preparation_error">Kitchen Preparation Error / Burn</option>
                  <option value="customer_leftover">Customer Plate Leftovers</option>
                  <option value="spoilage">Storage Spoilage</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Shift Notes</label>
                <input
                  type="text"
                  placeholder="e.g. Sudden rainstorm lowered late walk-ins"
                  value={formNotes}
                  onChange={(e) => setFormNotes(e.target.value)}
                  className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2 text-slate-800"
                />
              </div>

              {formSuccess && (
                <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-xs font-medium flex items-center space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                  <span>{formSuccess}</span>
                </div>
              )}

              <div className="flex items-center justify-end space-x-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowLogModal(false)}
                  className="px-4 py-2 border border-slate-300 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-semibold transition-colors"
                >
                  {submitting ? 'Saving...' : 'Submit Shift Log'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
