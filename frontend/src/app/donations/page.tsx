'use client';

import React, { useState, useEffect } from 'react';
import {
  HeartHandshake,
  ShieldCheck,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Building,
  UserCheck,
  Send,
  Leaf
} from 'lucide-react';
import { api } from '@/lib/api';
import { SurplusCandidate, DonationRecord } from '@/lib/types';

export default function SurplusDonationsPage() {
  const branchId = 'branch-downtown-01';
  const [candidates, setCandidates] = useState<SurplusCandidate[]>([]);
  const [donations, setDonations] = useState<DonationRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Verification modal state
  const [selectedCandidate, setSelectedCandidate] = useState<SurplusCandidate | null>(null);
  const [certifiedBy, setCertifiedBy] = useState<string>('Chef Marcus Vane');
  const [tempCelsius, setTempCelsius] = useState<number>(68.0);
  const [visualPassed, setVisualPassed] = useState<boolean>(true);
  const [packagingIntact, setPackagingIntact] = useState<boolean>(true);
  const [selectedNgo, setSelectedNgo] = useState<string>('City Harvest Community Food Bank');
  const [contactPhone, setContactPhone] = useState<string>('+1-555-019-2831');
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [statusMsg, setStatusMsg] = useState<string>('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [candRes, donRes] = await Promise.all([
        api.getSurplusCandidates(branchId).catch(() => []),
        api.getDonations(branchId).catch(() => []),
      ]);
      setCandidates(candRes);
      setDonations(donRes);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleDispatch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCandidate) return;
    setSubmitting(true);
    try {
      await api.certifyAndDispatchDonation({
        branch_id: branchId,
        menu_item_id: selectedCandidate.menu_item_id,
        surplus_quantity: selectedCandidate.surplus_quantity,
        certified_by: certifiedBy,
        temperature_verified_celsius: tempCelsius,
        visual_inspection_passed: visualPassed,
        packaging_intact: packagingIntact,
        recipient_ngo: selectedNgo,
        contact_phone: contactPhone,
      });
      setStatusMsg('Food safety certification verified. NGO pickup scheduled.');
      setTimeout(() => {
        setStatusMsg('');
        setSelectedCandidate(null);
        loadData();
      }, 1500);
    } catch (err: any) {
      alert(`Dispatch error: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Surplus Food & NGO Donation Workflow</h1>
        <p className="text-sm text-slate-500 mt-1">
          Coordinate safe surplus redistribution to vetted food relief shelters with mandatory food-safety verification checkpoints.
        </p>
      </div>

      {/* Food Safety Principle Alert */}
      <div className="bg-amber-50 border border-amber-200 p-4 rounded-xl text-xs text-amber-950 flex items-start space-x-3">
        <ShieldCheck className="w-5 h-5 text-amber-700 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-amber-900 block">Crucial Food Safety Principle</span>
          <p className="mt-0.5 text-amber-800 leading-relaxed">
            The software assists surplus detection and logistics, but does <strong>NOT</strong> independently certify microbiological food safety. All surplus donations require physical verification and sign-off by certified kitchen personnel.
          </p>
        </div>
      </div>

      {/* Surplus Candidates Grid */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-bold text-slate-900">Detected Clean Kitchen Surplus</h2>
            <p className="text-xs text-slate-500">Unsold portions from current shift eligible for donation or evening flash-discount</p>
          </div>
          <span className="text-xs bg-emerald-50 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded-full font-semibold">
            {candidates.length} Item(s) Available
          </span>
        </div>

        {candidates.length === 0 ? (
          <div className="py-8 text-center text-slate-400 text-xs">
            No unallocated surplus detected from recent kitchen shifts.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {candidates.map((cand) => (
              <div
                key={cand.menu_item_id}
                className="p-4 rounded-xl border border-slate-200 bg-slate-50 flex flex-col justify-between text-xs space-y-3"
              >
                <div>
                  <div className="flex items-start justify-between">
                    <h3 className="font-bold text-slate-900 text-sm">{cand.menu_item_name}</h3>
                    <span className="font-bold text-slate-900 bg-white px-2 py-0.5 rounded border border-slate-200">
                      {cand.surplus_quantity} {cand.unit}
                    </span>
                  </div>
                  <p className="text-slate-500 mt-1">
                    Shelf life remaining: ~{cand.estimated_shelf_life_remaining_hours} hours
                  </p>

                  <div className="mt-3 space-y-1 text-slate-600 bg-white p-2.5 rounded-lg border border-slate-100">
                    <div className="flex justify-between">
                      <span>Recommended for Flash Discount:</span>
                      <strong className="text-slate-800">{cand.recommended_discount_portion} portions</strong>
                    </div>
                    <div className="flex justify-between text-emerald-700 font-medium">
                      <span>Recommended for Shelter Donation:</span>
                      <strong>{cand.recommended_donation_portion} portions</strong>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => setSelectedCandidate(cand)}
                  className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-2 rounded-lg text-xs transition-colors flex items-center justify-center space-x-1.5"
                >
                  <ShieldCheck className="w-4 h-4" />
                  <span>Verify Safety & Dispatch &rarr;</span>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Dispatched Donations History & NGO Status */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
        <h2 className="text-base font-bold text-slate-900 mb-3">Redistribution Logistics & NGO Pickup Tracker</h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-100 text-xs font-semibold text-slate-400 uppercase">
                <th className="pb-3">Menu Item</th>
                <th className="pb-3">Quantity</th>
                <th className="pb-3">Recipient Partner</th>
                <th className="pb-3">Certified By</th>
                <th className="pb-3">Meals Saved</th>
                <th className="pb-3">CO2e Avoided</th>
                <th className="pb-3">Pickup Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {donations.map((d) => (
                <tr key={d.id} className="hover:bg-slate-50/60">
                  <td className="py-3 font-semibold text-slate-900">{d.menu_item_name}</td>
                  <td className="py-3 text-slate-800">
                    {d.surplus_quantity} {d.unit}
                  </td>
                  <td className="py-3 text-xs text-slate-600">{d.recipient_ngo}</td>
                  <td className="py-3 text-xs text-slate-500">{d.certified_by}</td>
                  <td className="py-3 text-xs font-bold text-emerald-600">+{d.impact_meals_saved} meals</td>
                  <td className="py-3 text-xs text-slate-600">~{d.carbon_avoided_kg} kg</td>
                  <td className="py-3">
                    <span
                      className={`text-[11px] font-semibold px-2 py-0.5 rounded-full capitalize ${
                        d.pickup_status === 'delivered' || d.pickup_status === 'picked_up'
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : 'bg-blue-50 text-blue-700 border border-blue-200'
                      }`}
                    >
                      {d.pickup_status}
                    </span>
                  </td>
                </tr>
              ))}
              {donations.length === 0 && (
                <tr>
                  <td colSpan={7} className="py-6 text-center text-xs text-slate-400">
                    No donations dispatched yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Safety Verification & Dispatch Modal */}
      {selectedCandidate && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl border border-slate-200">
            <h3 className="text-lg font-bold text-slate-900">Food Safety Verification & NGO Handover</h3>
            <p className="text-xs text-slate-500 mt-1">
              Confirm thermal and sensory checks for {selectedCandidate.surplus_quantity} portions of {selectedCandidate.menu_item_name}.
            </p>

            <form onSubmit={handleDispatch} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Certifying Authorized Kitchen Staff
                </label>
                <input
                  type="text"
                  required
                  value={certifiedBy}
                  onChange={(e) => setCertifiedBy(e.target.value)}
                  className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2 text-slate-800"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Holding Temperature Verification (°C)
                </label>
                <input
                  type="number"
                  step="0.5"
                  required
                  value={tempCelsius}
                  onChange={(e) => setTempCelsius(parseFloat(e.target.value) || 0)}
                  className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2 text-slate-800"
                />
                <span className="text-[11px] text-slate-400">Food code: Hot holding ≥ 60°C or cold chill ≤ 4°C</span>
              </div>

              <div className="space-y-2 bg-slate-50 p-3 rounded-xl border border-slate-200">
                <label className="flex items-center text-xs font-medium text-slate-700 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={visualPassed}
                    onChange={(e) => setVisualPassed(e.target.checked)}
                    className="mr-2 text-emerald-600 rounded"
                  />
                  <span>Visual and sensory inspection passed (no discoloration, aroma normal)</span>
                </label>

                <label className="flex items-center text-xs font-medium text-slate-700 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={packagingIntact}
                    onChange={(e) => setPackagingIntact(e.target.checked)}
                    className="mr-2 text-emerald-600 rounded"
                  />
                  <span>Packaging sealed, sanitized, and labeled with date/time of preparation</span>
                </label>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Partner Relief NGO</label>
                <select
                  value={selectedNgo}
                  onChange={(e) => setSelectedNgo(e.target.value)}
                  className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2 text-slate-800"
                >
                  <option value="City Harvest Community Food Bank">City Harvest Community Food Bank</option>
                  <option value="Feeding Families Shelter Network">Feeding Families Shelter Network</option>
                  <option value="No Waste Kitchen Coalition">No Waste Kitchen Coalition</option>
                </select>
              </div>

              {statusMsg && (
                <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-xs font-medium flex items-center space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                  <span>{statusMsg}</span>
                </div>
              )}

              <div className="flex items-center justify-end space-x-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setSelectedCandidate(null)}
                  className="px-4 py-2 border border-slate-300 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting || !visualPassed || !packagingIntact}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-semibold transition-colors disabled:opacity-50"
                >
                  {submitting ? 'Dispatching...' : 'Certify & Request Pickup'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
