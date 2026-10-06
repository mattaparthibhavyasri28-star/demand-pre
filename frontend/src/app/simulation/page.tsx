'use client';

import React, { useState, useEffect } from 'react';
import {
  Sliders,
  CloudRain,
  Calendar,
  Sparkles,
  AlertTriangle,
  Info,
  ArrowRight,
  TrendingUp,
  Percent
} from 'lucide-react';
import { api } from '@/lib/api';
import { WhatIfSimulationResponse } from '@/lib/types';

export default function WhatIfSimulatorPage() {
  const branchId = 'branch-downtown-01';
  const [targetDate, setTargetDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [weatherScenario, setWeatherScenario] = useState<string>('Heavy Rain');
  const [isHoliday, setIsHoliday] = useState<boolean>(false);
  const [isFestival, setIsFestival] = useState<boolean>(false);
  const [activePromotion, setActivePromotion] = useState<boolean>(false);
  const [demandShift, setDemandShift] = useState<number>(0);

  const [simulation, setSimulation] = useState<WhatIfSimulationResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const runSim = async () => {
    setLoading(true);
    try {
      const res = await api.runSimulation({
        branch_id: branchId,
        target_date: targetDate,
        weather_scenario: weatherScenario,
        is_holiday: isHoliday,
        active_promotion: activePromotion,
        demand_shift_percentage: demandShift
      });
      setSimulation(res);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runSim();
  }, [weatherScenario, isHoliday, isFestival, activePromotion, demandShift, targetDate]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">What-If Scenario Simulator</h1>
        <p className="text-sm text-slate-500 mt-1">
          Stress-test tomorrow's kitchen preparation against weather events, holidays, promotional spikes, and demand shifts.
        </p>
      </div>

      {/* Simulator Control Panel */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs space-y-5">
        <h2 className="text-base font-bold text-slate-900 flex items-center space-x-2">
          <Sliders className="w-4 h-4 text-emerald-600" />
          <span>Scenario Variables</span>
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Weather Event</label>
            <select
              value={weatherScenario}
              onChange={(e) => setWeatherScenario(e.target.value)}
              className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2 text-slate-800"
            >
              <option value="Clear">Clear & Mild (Standard)</option>
              <option value="Light Rain">Light Rain Showers</option>
              <option value="Heavy Rain">Heavy Torrential Rain (28mm)</option>
              <option value="Heatwave">Summer Heatwave (36°C)</option>
              <option value="Cold Snap">Winter Cold Snap (12°C)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Manual Demand Stress-Test</label>
            <div className="flex items-center space-x-3">
              <input
                type="range"
                min="-30"
                max="30"
                step="5"
                value={demandShift}
                onChange={(e) => setDemandShift(parseFloat(e.target.value))}
                className="w-full accent-emerald-600"
              />
              <span className="text-xs font-bold w-12 text-right">
                {demandShift > 0 ? `+${demandShift}%` : `${demandShift}%`}
              </span>
            </div>
          </div>

          <div className="flex flex-col justify-end space-y-2">
            <label className="inline-flex items-center cursor-pointer text-xs font-semibold text-slate-700">
              <input
                type="checkbox"
                checked={isHoliday}
                onChange={(e) => setIsHoliday(e.target.checked)}
                className="rounded border-slate-300 text-emerald-600 mr-2"
              />
              <span>Public Holiday</span>
            </label>

            <label className="inline-flex items-center cursor-pointer text-xs font-semibold text-slate-700">
              <input
                type="checkbox"
                checked={activePromotion}
                onChange={(e) => setActivePromotion(e.target.checked)}
                className="rounded border-slate-300 text-emerald-600 mr-2"
              />
              <span>Active Promotion (e.g. 20% Off)</span>
            </label>
          </div>

          <div className="flex items-end">
            <button
              onClick={runSim}
              disabled={loading}
              className="w-full bg-slate-900 hover:bg-slate-800 text-white font-semibold px-4 py-2 rounded-lg text-sm transition-colors flex items-center justify-center space-x-2"
            >
              <span>{loading ? 'Simulating...' : 'Recalculate Impact'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Simulation Results Banner */}
      {simulation && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
            <div className="bg-white p-4 rounded-xl border border-slate-200">
              <span className="text-xs text-slate-500 font-medium">Baseline Demand</span>
              <div className="mt-2 text-2xl font-bold text-slate-800">
                {Math.round(simulation.total_baseline_demand)} portions
              </div>
              <span className="text-xs text-slate-400">Normal run rate</span>
            </div>

            <div className="bg-white p-4 rounded-xl border border-slate-200">
              <span className="text-xs text-slate-500 font-medium">Simulated Demand</span>
              <div className="mt-2 text-2xl font-bold text-emerald-600">
                {Math.round(simulation.total_simulated_demand)} portions
              </div>
              <span className="text-xs text-emerald-700 font-semibold">
                {simulation.net_demand_change_pct > 0 ? `+${simulation.net_demand_change_pct}%` : `${simulation.net_demand_change_pct}%`} net shift
              </span>
            </div>

            <div className="bg-white p-4 rounded-xl border border-slate-200">
              <span className="text-xs text-slate-500 font-medium">Estimated Waste Risk</span>
              <div className="mt-2 text-2xl font-bold text-rose-600">
                {simulation.total_estimated_waste_risk} portions
              </div>
              <span className="text-xs text-slate-400">Potential excess if unadjusted</span>
            </div>

            <div className="bg-white p-4 rounded-xl border border-slate-200">
              <span className="text-xs text-slate-500 font-medium">Scenario Status</span>
              <div className="mt-2 text-sm font-bold text-slate-900 line-clamp-1">
                {simulation.scenario_description.split('|')[0]}
              </div>
              <span className="text-xs text-slate-500 mt-1 block">Stress test evaluated</span>
            </div>
          </div>

          {/* Key Drivers Alert */}
          <div className="bg-slate-900 text-white p-4 rounded-xl text-xs space-y-1.5">
            <span className="font-bold text-emerald-400 uppercase tracking-wider block">Key Operational Drivers</span>
            {simulation.key_drivers.map((kd, idx) => (
              <p key={idx} className="text-slate-300">&bull; {kd}</p>
            ))}
          </div>

          {/* Item by Item Table */}
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
            <h2 className="text-base font-bold text-slate-900 mb-3">Item-Level Simulation Impact & Prep Guidance</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-100 text-xs font-semibold text-slate-400 uppercase">
                    <th className="pb-3">Menu Item</th>
                    <th className="pb-3">Baseline</th>
                    <th className="pb-3">Simulated Demand</th>
                    <th className="pb-3">Change %</th>
                    <th className="pb-3">Recommended Prep</th>
                    <th className="pb-3">Waste Risk</th>
                    <th className="pb-3">Risk Level</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {simulation.item_simulations.map((item) => (
                    <tr key={item.menu_item_id} className="hover:bg-slate-50/60">
                      <td className="py-3 font-semibold text-slate-900">{item.menu_item_name}</td>
                      <td className="py-3 text-slate-600">{Math.round(item.baseline_demand)}</td>
                      <td className="py-3 font-bold text-slate-900">{Math.round(item.simulated_demand)}</td>
                      <td className="py-3 text-xs font-semibold">
                        <span className={item.demand_change_percentage > 0 ? 'text-emerald-600' : item.demand_change_percentage < 0 ? 'text-rose-600' : 'text-slate-500'}>
                          {item.demand_change_percentage > 0 ? `+${item.demand_change_percentage}%` : `${item.demand_change_percentage}%`}
                        </span>
                      </td>
                      <td className="py-3 font-medium text-slate-800">
                        <span className="px-2 py-0.5 rounded bg-slate-100 border border-slate-200">
                          {item.recommended_preparation} portions
                        </span>
                      </td>
                      <td className="py-3 text-xs text-rose-600 font-medium">
                        {item.predicted_waste_risk_portions} portions
                      </td>
                      <td className="py-3">
                        <span
                          className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                            item.risk_level === 'high'
                              ? 'bg-rose-50 text-rose-700 border border-rose-200'
                              : item.risk_level === 'moderate'
                              ? 'bg-amber-50 text-amber-700 border border-amber-200'
                              : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          }`}
                        >
                          {item.risk_level}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Mandatory Disclaimer */}
          <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-900 flex items-start space-x-2">
            <Info className="w-4 h-4 text-amber-700 flex-shrink-0 mt-0.5" />
            <p>
              <strong>Methodology Notice:</strong> {simulation.disclaimer}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
