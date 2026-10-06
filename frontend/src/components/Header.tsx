'use client';

import React from 'react';
import { Store, ShieldCheck, Activity } from 'lucide-react';

export function Header() {
  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-10">
      <div className="flex items-center space-x-3">
        <div className="flex items-center space-x-2 text-sm text-slate-700 bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200">
          <Store className="w-4 h-4 text-emerald-600" />
          <span className="font-semibold">The Green Plate Bistro</span>
          <span className="text-slate-400">/</span>
          <span className="text-slate-600">Downtown Flagship</span>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-1.5 text-xs text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
          <Activity className="w-3.5 h-3.5 animate-pulse text-emerald-600" />
          <span className="font-medium">System Online (FastAPI + Supabase)</span>
        </div>

        <div className="flex items-center space-x-1.5 text-xs text-slate-500 bg-slate-50 px-2.5 py-1 rounded-full border border-slate-200">
          <ShieldCheck className="w-3.5 h-3.5 text-blue-600" />
          <span>Role: Restaurant Manager</span>
        </div>
      </div>
    </header>
  );
}
