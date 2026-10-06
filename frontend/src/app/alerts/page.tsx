'use client';

import React, { useState, useEffect } from 'react';
import {
  Bell,
  AlertTriangle,
  AlertOctagon,
  Info,
  CheckCircle,
  Filter,
  Check
} from 'lucide-react';
import { api } from '@/lib/api';
import { AlertItem } from '@/lib/types';

export default function OperationalAlertsPage() {
  const branchId = 'branch-downtown-01';
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [filter, setFilter] = useState<'all' | 'active' | 'acknowledged'>('all');
  const [loading, setLoading] = useState<boolean>(true);

  const loadAlerts = async () => {
    setLoading(true);
    try {
      const res = await api.getAlerts(branchId);
      setAlerts(res);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, []);

  const handleAcknowledge = async (alertId: string) => {
    try {
      await api.acknowledgeAlert(alertId);
      loadAlerts();
    } catch (err: any) {
      alert(`Action error: ${err.message}`);
    }
  };

  const filtered = alerts.filter((a) => {
    if (filter === 'all') return true;
    return a.status === filter;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Operational Alerts & Threshold Intelligence</h1>
          <p className="text-sm text-slate-500 mt-1">
            Data-derived alerts monitoring waste risk thresholds, safety stock depletion, and ingredient shelf-life expiries.
          </p>
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center space-x-2 bg-slate-100 p-1 rounded-xl text-xs font-semibold">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1.5 rounded-lg transition-colors ${
              filter === 'all' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            All ({alerts.length})
          </button>
          <button
            onClick={() => setFilter('active')}
            className={`px-3 py-1.5 rounded-lg transition-colors ${
              filter === 'active' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Active ({alerts.filter((a) => a.status === 'active').length})
          </button>
          <button
            onClick={() => setFilter('acknowledged')}
            className={`px-3 py-1.5 rounded-lg transition-colors ${
              filter === 'acknowledged' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Acknowledged
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-400">Loading alerts...</div>
      ) : (
        <div className="space-y-3">
          {filtered.map((item) => (
            <div
              key={item.id}
              className={`p-4 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-all ${
                item.severity === 'critical'
                  ? 'bg-rose-50/70 border-rose-200'
                  : item.severity === 'warning'
                  ? 'bg-amber-50/70 border-amber-200'
                  : 'bg-blue-50/70 border-blue-200'
              }`}
            >
              <div className="flex items-start space-x-3">
                <div className="mt-0.5">
                  {item.severity === 'critical' ? (
                    <AlertOctagon className="w-5 h-5 text-rose-600" />
                  ) : item.severity === 'warning' ? (
                    <AlertTriangle className="w-5 h-5 text-amber-600" />
                  ) : (
                    <Info className="w-5 h-5 text-blue-600" />
                  )}
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-slate-900 text-sm">{item.title}</span>
                    <span
                      className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                        item.severity === 'critical'
                          ? 'bg-rose-100 text-rose-800'
                          : item.severity === 'warning'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-blue-100 text-blue-800'
                      }`}
                    >
                      {item.severity}
                    </span>
                    <span className="text-[11px] text-slate-400 capitalize">
                      &bull; {item.alert_type.replace('_', ' ')}
                    </span>
                  </div>
                  <p className="text-xs text-slate-700 mt-1 leading-relaxed max-w-3xl">{item.message}</p>
                </div>
              </div>

              <div className="flex items-center space-x-3 self-end sm:self-center flex-shrink-0">
                {item.status === 'active' ? (
                  <button
                    onClick={() => handleAcknowledge(item.id)}
                    className="px-3 py-1.5 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-semibold rounded-lg transition-colors flex items-center space-x-1 shadow-2xs"
                  >
                    <Check className="w-3.5 h-3.5 text-emerald-600" />
                    <span>Acknowledge</span>
                  </button>
                ) : (
                  <span className="text-xs text-emerald-700 font-medium bg-emerald-50 px-2.5 py-1 rounded-md border border-emerald-200">
                    Acknowledged
                  </span>
                )}
              </div>
            </div>
          ))}

          {filtered.length === 0 && (
            <div className="text-center py-12 bg-white rounded-xl border border-slate-200 text-slate-400 text-xs">
              No alerts matching the selected filter.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
