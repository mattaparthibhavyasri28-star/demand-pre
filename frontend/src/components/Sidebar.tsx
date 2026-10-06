'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  TrendingUp,
  PackageSearch,
  Trash2,
  Sliders,
  HeartHandshake,
  Leaf,
  Receipt,
  Bell,
  Sparkles,
  Bot
} from 'lucide-react';

const NAV_ITEMS = [
  { href: '/', label: 'Overview', icon: LayoutDashboard },
  { href: '/forecast', label: 'Demand Forecast', icon: TrendingUp },
  { href: '/copilot', label: 'AI Copilot (NVIDIA)', icon: Bot },
  { href: '/inventory', label: 'Smart Inventory', icon: PackageSearch },
  { href: '/waste', label: 'Waste Tracking', icon: Trash2 },
  { href: '/simulation', label: 'What-If Simulator', icon: Sliders },
  { href: '/donations', label: 'Surplus & Donations', icon: HeartHandshake },
  { href: '/sustainability', label: 'Sustainability Impact', icon: Leaf },
  { href: '/pos', label: 'POS Integration', icon: Receipt },
  { href: '/alerts', label: 'Alerts', icon: Bell },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-slate-900 text-slate-100 flex flex-col flex-shrink-0 min-h-screen border-r border-slate-800">
      <div className="p-5 border-b border-slate-800 flex items-center space-x-3">
        <div className="p-2 bg-emerald-500 rounded-lg text-slate-950 font-bold">
          <Sparkles className="w-5 h-5" />
        </div>
        <div>
          <h1 className="font-bold text-base tracking-tight leading-none text-white">EcoKitchen AI</h1>
          <p className="text-xs text-slate-400 mt-1">Demand & Waste Decision Support</p>
        </div>
      </div>

      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-800 bg-slate-950/40 text-xs text-slate-400">
        <div className="flex items-center justify-between">
          <span>ML Feedback Loop</span>
          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800">
            Active (XGBoost)
          </span>
        </div>
        <p className="mt-1 text-[11px] text-slate-400">Continuous calibration enabled</p>
      </div>
    </aside>
  );
}
