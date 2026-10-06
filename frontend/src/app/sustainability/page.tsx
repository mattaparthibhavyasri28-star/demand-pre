'use client';

import React, { useState, useEffect } from 'react';
import {
  Leaf,
  Droplet,
  CloudLightning,
  DollarSign,
  Heart,
  TrendingDown,
  Info,
  ShieldCheck
} from 'lucide-react';
import { api } from '@/lib/api';
import { SustainabilitySummary } from '@/lib/types';

export default function SustainabilityDashboardPage() {
  const branchId = 'branch-downtown-01';
  const [data, setData] = useState<SustainabilitySummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadSustainability() {
      try {
        const res = await api.getSustainability(branchId, 30);
        setData(res);
      } finally {
        setLoading(false);
      }
    }
    loadSustainability();
  }, []);

  if (loading) {
    return <div className="text-center py-12 text-slate-500">Calculating environmental life-cycle savings...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Sustainability & ESG Impact Dashboard</h1>
        <p className="text-sm text-slate-500 mt-1">
          Measurable sustainability dividends from demand precision, kitchen batch trimming, and surplus food redistribution.
        </p>
      </div>

      {/* Top Impact Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">CO2e Emissions Avoided</span>
            <div className="p-2 bg-emerald-50 text-emerald-600 rounded-lg">
              <Leaf className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">
              {data?.estimated_co2e_avoided_kg.toLocaleString()}
            </span>
            <span className="text-xs text-slate-500">kg CO2e</span>
          </div>
          <span className="text-[11px] text-emerald-600 font-medium mt-1 block">
            Diverted from landfill decomposition
          </span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Embedded Water Saved</span>
            <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
              <Droplet className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">
              {data?.estimated_water_saved_liters.toLocaleString()}
            </span>
            <span className="text-xs text-slate-500">Liters</span>
          </div>
          <span className="text-[11px] text-blue-600 font-medium mt-1 block">
            Agricultural irrigation footprint
          </span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Diverted Meals for Relief</span>
            <div className="p-2 bg-rose-50 text-rose-600 rounded-lg">
              <Heart className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">{data?.meals_donated_to_ngos}</span>
            <span className="text-xs text-slate-500">meals donated</span>
          </div>
          <span className="text-[11px] text-rose-600 font-medium mt-1 block">
            Delivered to community food banks
          </span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Operating Cost Saved</span>
            <div className="p-2 bg-amber-50 text-amber-600 rounded-lg">
              <DollarSign className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">
              ${data?.estimated_cost_saved_usd.toLocaleString()}
            </span>
            <span className="text-xs text-slate-500">USD</span>
          </div>
          <span className="text-[11px] text-emerald-600 font-medium mt-1 block">
            Direct ingredient loss reduction
          </span>
        </div>
      </div>

      {/* Environmental Methodologies & Calculations Card */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs space-y-4">
        <h2 className="text-base font-bold text-slate-900">Life-Cycle Assessment (LCA) Factors</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {data?.environmental_factors.map((factor, idx) => (
            <div key={idx} className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-2 text-xs">
              <span className="font-bold text-slate-900 block text-sm">{factor.category}</span>
              <div className="flex items-baseline space-x-1">
                <span className="text-xl font-extrabold text-emerald-700">
                  {factor.amount_saved.toLocaleString()}
                </span>
                <span className="text-slate-500 font-semibold">{factor.unit}</span>
              </div>
              <p className="text-slate-600 text-[11px] leading-relaxed pt-2 border-t border-slate-200">
                <strong>Source:</strong> {factor.methodology}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Mandatory Scientific Disclaimer */}
      <div className="p-4 bg-slate-100 border border-slate-200 rounded-xl text-xs text-slate-700 flex items-start space-x-3">
        <Info className="w-5 h-5 text-slate-500 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-slate-900 block">Methodological Transparency Statement</span>
          <p className="mt-0.5 leading-relaxed text-slate-600">
            {data?.methodology_statement ||
              'Environmental savings are model-estimated based on USDA & WRI life-cycle analysis factors (~2.5 kg CO2e / kg food, 1000L water / kg food) and decision-support data, not direct physical sensors.'}
          </p>
        </div>
      </div>
    </div>
  );
}
