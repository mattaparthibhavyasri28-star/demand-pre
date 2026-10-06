'use client';

import React, { useState } from 'react';
import {
  Receipt,
  UploadCloud,
  CheckCircle2,
  AlertCircle,
  FileText,
  Zap,
  Clock,
  ArrowRight
} from 'lucide-react';
import { api } from '@/lib/api';

export default function POSIntegrationPage() {
  const branchId = 'branch-downtown-01';

  // Live POS Simulator State
  const [menuItemId, setMenuItemId] = useState<string>('item-biryani-01');
  const [quantity, setQuantity] = useState<number>(3);
  const [unitPrice, setUnitPrice] = useState<number>(14.50);
  const [simulating, setSimulating] = useState<boolean>(false);
  const [liveMsg, setLiveMsg] = useState<string>('');

  // CSV Upload State
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadResult, setUploadResult] = useState<string>('');

  const handleFirePOSEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    setSimulating(true);
    try {
      const res = await api.sendMockPOSEvent({
        branch_id: branchId,
        menu_item_id: menuItemId,
        sale_date: new Date().toISOString().split('T')[0],
        sale_hour: new Date().getHours(),
        quantity_sold: quantity,
        unit_price: unitPrice,
      });
      setLiveMsg(`Transaction verified! Ingested ${quantity} portion(s) into sales stream.`);
      setTimeout(() => setLiveMsg(''), 3000);
    } catch (err: any) {
      alert(`POS Webhook Error: ${err.message}`);
    } finally {
      setSimulating(false);
    }
  };

  const handleUploadCsv = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!csvFile) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('branch_id', branchId);
      formData.append('file', csvFile);

      const res = await fetch('http://127.0.0.1:8000/api/v1/pos/upload-csv', {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) {
        const err = await res.text();
        throw new Error(err);
      }
      const data = await res.json();
      setUploadResult(`Successfully imported ${data.records_imported} sales records from ${data.filename}.`);
      setCsvFile(null);
    } catch (err: any) {
      setUploadResult(`Upload error: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">POS Integration & Sales Data Ingestion</h1>
        <p className="text-sm text-slate-500 mt-1">
          P2 — Multi-modal sales ingestion via Batch CSV uploads, cloud POS webhooks (Toast, Square, Clover), and real-time streaming.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* CSV Batch Upload Section */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-2 text-slate-900 font-bold text-base mb-1">
              <UploadCloud className="w-5 h-5 text-emerald-600" />
              <h2>Batch CSV / Daily Register Upload</h2>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Import historical or daily closing sales spreadsheets directly into the PostgreSQL data pipeline.
            </p>

            <form onSubmit={handleUploadCsv} className="space-y-4">
              <div className="border-2 border-dashed border-slate-200 rounded-xl p-6 text-center hover:bg-slate-50/50 transition-colors">
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => setCsvFile(e.target.files?.[0] || null)}
                  className="hidden"
                  id="csv-file-input"
                />
                <label htmlFor="csv-file-input" className="cursor-pointer">
                  <FileText className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                  <span className="text-xs font-semibold text-emerald-600 hover:underline">
                    {csvFile ? csvFile.name : 'Choose CSV file to upload'}
                  </span>
                  <p className="text-[11px] text-slate-400 mt-1">
                    Columns: menu_item_id, date, quantity_sold, unit_price
                  </p>
                </label>
              </div>

              {uploadResult && (
                <div
                  className={`p-3 rounded-lg text-xs font-medium ${
                    uploadResult.includes('Successfully')
                      ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                      : 'bg-rose-50 text-rose-800 border border-rose-200'
                  }`}
                >
                  {uploadResult}
                </div>
              )}

              <button
                type="submit"
                disabled={!csvFile || uploading}
                className="w-full bg-slate-900 hover:bg-slate-800 text-white font-semibold py-2.5 rounded-xl text-sm transition-colors disabled:opacity-50"
              >
                {uploading ? 'Processing File...' : 'Upload & Process Batch'}
              </button>
            </form>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-100 text-xs text-slate-500 space-y-1">
            <span className="font-semibold text-slate-700 block">Accepted Columns Schema:</span>
            <code className="text-[11px] bg-slate-100 p-1 rounded text-slate-700 block">
              date, menu_item_id, quantity_sold, unit_price, weather_temp, rainfall_mm
            </code>
          </div>
        </div>

        {/* Real-Time POS Webhook Event Simulator */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-2 text-slate-900 font-bold text-base mb-1">
              <Zap className="w-5 h-5 text-amber-500" />
              <h2>Live POS Webhook Event Simulator</h2>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Simulate instant live register ring-ups to test Near-Real-Time demand recalibration.
            </p>

            <form onSubmit={handleFirePOSEvent} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Menu Item Ordered</label>
                <select
                  value={menuItemId}
                  onChange={(e) => {
                    const id = e.target.value;
                    setMenuItemId(id);
                    if (id.includes('biryani')) setUnitPrice(14.50);
                    else if (id.includes('paneer')) setUnitPrice(12.00);
                    else if (id.includes('salmon')) setUnitPrice(22.00);
                    else if (id.includes('pizza')) setUnitPrice(11.50);
                    else setUnitPrice(9.50);
                  }}
                  className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2 text-slate-800"
                >
                  <option value="item-biryani-01">Chicken Biryani ($14.50)</option>
                  <option value="item-paneer-02">Paneer Butter Masala ($12.00)</option>
                  <option value="item-friedrice-03">Veg Fried Rice ($9.50)</option>
                  <option value="item-salmon-04">Grilled Salmon ($22.00)</option>
                  <option value="item-pizza-05">Margherita Pizza ($11.50)</option>
                  <option value="item-salad-06">Caesar Salad ($8.50)</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Quantity Sold</label>
                  <input
                    type="number"
                    min="1"
                    max="20"
                    value={quantity}
                    onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
                    className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2 text-slate-800"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Unit Price ($)</label>
                  <input
                    type="number"
                    step="0.5"
                    value={unitPrice}
                    onChange={(e) => setUnitPrice(parseFloat(e.target.value) || 0)}
                    className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2 text-slate-800"
                  />
                </div>
              </div>

              {liveMsg && (
                <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-xs font-medium flex items-center space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                  <span>{liveMsg}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={simulating}
                className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-2.5 rounded-xl text-sm transition-colors flex items-center justify-center space-x-2 shadow-xs"
              >
                <Zap className="w-4 h-4" />
                <span>{simulating ? 'Transmitting...' : 'Dispatch POS Transaction'}</span>
              </button>
            </form>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-100 text-xs text-slate-400">
            Endpoint: <code className="text-slate-600">POST /api/v1/pos/webhook</code>
          </div>
        </div>
      </div>
    </div>
  );
}
