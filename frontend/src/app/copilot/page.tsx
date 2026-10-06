'use client';

import React, { useState, useEffect } from 'react';
import {
  Bot,
  Sparkles,
  Zap,
  Cpu,
  ChefHat,
  MessageSquare,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  KeyRound,
  ArrowRight
} from 'lucide-react';

interface CopilotStatus {
  is_llm_configured: boolean;
  provider: string;
  model: string;
  base_url: string;
  free_tier_available: boolean;
  instructions: string;
}

export default function AICopilotPage() {
  const branchId = 'branch-downtown-01';
  const [status, setStatus] = useState<CopilotStatus | null>(null);
  const [briefing, setBriefing] = useState<string>('');
  const [briefingSource, setBriefingSource] = useState<string>('');
  const [loadingBriefing, setLoadingBriefing] = useState<boolean>(false);

  // Surplus Repurposing Tool
  const [repurposeItem, setRepurposeItem] = useState<string>('Chicken Biryani');
  const [repurposeQty, setRepurposeQty] = useState<number>(14);
  const [repurposePlan, setRepurposePlan] = useState<string>('');
  const [loadingRepurpose, setLoadingRepurpose] = useState<boolean>(false);

  // Interactive Chat / Q&A
  const [chatQuery, setChatQuery] = useState<string>('');
  const [chatResponse, setChatResponse] = useState<string>('');
  const [loadingChat, setLoadingChat] = useState<boolean>(false);

  useEffect(() => {
    async function loadStatus() {
      try {
        const res = await fetch('http://127.0.0.1:8000/api/v1/copilot/status');
        if (res.ok) {
          const data = await res.json();
          setStatus(data);
        }
      } catch (e) {
        console.error(e);
      }
    }
    loadStatus();
  }, []);

  const handleFetchBriefing = async () => {
    setLoadingBriefing(true);
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/copilot/daily-briefing?branch_id=${branchId}`);
      if (res.ok) {
        const data = await res.json();
        setBriefing(data.briefing_text);
        setBriefingSource(data.source);
      }
    } catch (e: any) {
      alert(`Error loading briefing: ${e.message}`);
    } finally {
      setLoadingBriefing(false);
    }
  };

  const handleRepurpose = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoadingRepurpose(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/copilot/surplus-repurpose', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          menu_item_name: repurposeItem,
          surplus_quantity: repurposeQty,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setRepurposePlan(data.repurposing_plan);
      }
    } catch (e: any) {
      alert(`Error: ${e.message}`);
    } finally {
      setLoadingRepurpose(false);
    }
  };

  const handleAskQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatQuery.trim()) return;
    setLoadingChat(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/copilot/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: chatQuery,
          branch_id: branchId,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setChatResponse(data.response);
      }
    } catch (e: any) {
      alert(`Error: ${e.message}`);
    } finally {
      setLoadingChat(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 flex items-center space-x-2">
          <Bot className="w-6 h-6 text-emerald-600" />
          <span>AI Kitchen Copilot</span>
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          NVIDIA NIM-powered conversational culinary operations assistant and surplus recipe repurposing engine.
        </p>
      </div>

      {/* Provider Status Card */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 rounded-2xl p-5 text-white shadow-sm border border-slate-700 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-emerald-400">
            <Zap className="w-4 h-4" />
            <span>Inference Microservice Engine</span>
          </div>
          <h2 className="text-lg font-bold">NVIDIA NIM • {status?.model || 'meta/llama-3.1-8b-instruct'}</h2>
          <p className="text-xs text-slate-300 max-w-2xl leading-relaxed">
            Ultra-low latency inference (~30-50ms TTFT). Designed to turn tabular ML forecasts and inventory metrics into executive chef operational directives.
          </p>
        </div>

        <div className="flex flex-col items-start md:items-end gap-1.5 flex-shrink-0">
          <span
            className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider flex items-center space-x-1.5 ${
              status?.is_llm_configured
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-current animate-pulse"></span>
            <span>{status?.is_llm_configured ? 'NVIDIA API Key Active' : 'Deterministic Rules Mode'}</span>
          </span>
          <span className="text-[11px] text-slate-400">
            {status?.is_llm_configured ? 'Live LLM microservice enabled' : 'Set NVIDIA_API_KEY in .env to enable LLM'}
          </span>
        </div>
      </div>

      {/* Grid: Daily Shift Briefing & Surplus Repurposing */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Shift Briefing */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <ChefHat className="w-5 h-5 text-emerald-600" />
                <h3 className="text-base font-bold text-slate-900">Executive Morning Chef Briefing</h3>
              </div>
              <button
                onClick={handleFetchBriefing}
                disabled={loadingBriefing}
                className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold transition-colors disabled:opacity-50"
              >
                {loadingBriefing ? 'Generating...' : 'Synthesize Briefing'}
              </button>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Transforms today's XGBoost portion forecasts, weather conditions, and inventory alerts into a concise 3-bullet morning kitchen brigade directive.
            </p>

            {briefing ? (
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-800 leading-relaxed space-y-2 whitespace-pre-line">
                {briefing}
                <div className="mt-3 pt-2 border-t border-slate-200 text-[10px] text-slate-400 flex items-center justify-between">
                  <span>Engine: {briefingSource}</span>
                  <span className="text-emerald-600 font-semibold">Ready for Pre-Shift Huddle</span>
                </div>
              </div>
            ) : (
              <div className="text-center py-10 bg-slate-50/50 rounded-xl border border-dashed border-slate-200 text-slate-400 text-xs">
                Click &ldquo;Synthesize Briefing&rdquo; to generate today&apos;s shift guidance.
              </div>
            )}
          </div>
        </div>

        {/* Chef Surplus Recipe Repurposing */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-2 mb-1">
              <Sparkles className="w-5 h-5 text-amber-500" />
              <h3 className="text-base font-bold text-slate-900">Surplus Recipe Repurposing Assistant</h3>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Suggests chef-approved ways to safely transform unsold cooked portions into profitable evening appetizers or side dishes.
            </p>

            <form onSubmit={handleRepurpose} className="grid grid-cols-2 gap-3 mb-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Surplus Dish</label>
                <select
                  value={repurposeItem}
                  onChange={(e) => setRepurposeItem(e.target.value)}
                  className="w-full text-xs border border-slate-300 rounded-lg px-2.5 py-2 text-slate-800"
                >
                  <option value="Chicken Biryani">Chicken Biryani</option>
                  <option value="Paneer Butter Masala">Paneer Butter Masala</option>
                  <option value="Veg Fried Rice">Veg Fried Rice</option>
                  <option value="Grilled Salmon">Grilled Salmon</option>
                  <option value="Margherita Pizza">Margherita Pizza</option>
                  <option value="Caesar Salad">Caesar Salad</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Unsold Portions</label>
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={repurposeQty}
                  onChange={(e) => setRepurposeQty(parseInt(e.target.value) || 1)}
                  className="w-full text-xs border border-slate-300 rounded-lg px-2.5 py-2 text-slate-800"
                />
              </div>

              <div className="col-span-2">
                <button
                  type="submit"
                  disabled={loadingRepurpose}
                  className="w-full bg-slate-900 hover:bg-slate-800 text-white rounded-lg py-2 text-xs font-semibold transition-colors disabled:opacity-50"
                >
                  {loadingRepurpose ? 'Analyzing Culinary Repurposing...' : 'Generate Repurposing Ideas'}
                </button>
              </div>
            </form>

            {repurposePlan && (
              <div className="p-3.5 rounded-xl bg-amber-50/60 border border-amber-200/80 text-xs text-slate-800 leading-relaxed whitespace-pre-line">
                {repurposePlan}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Interactive Kitchen Copilot Assistant */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs space-y-4">
        <div className="flex items-center space-x-2">
          <MessageSquare className="w-5 h-5 text-blue-600" />
          <h3 className="text-base font-bold text-slate-900">Ask the Kitchen Copilot</h3>
        </div>
        <p className="text-xs text-slate-500">
          Ask conversational questions regarding weather shock adjustments, stockout prevention, or waste reduction strategies.
        </p>

        <form onSubmit={handleAskQuestion} className="flex gap-2">
          <input
            type="text"
            placeholder="e.g. It is raining 25mm this afternoon. How should I adjust our dinner preparation batches?"
            value={chatQuery}
            onChange={(e) => setChatQuery(e.target.value)}
            className="flex-1 text-xs border border-slate-300 rounded-xl px-4 py-2.5 text-slate-800 focus:outline-emerald-600"
          />
          <button
            type="submit"
            disabled={loadingChat || !chatQuery.trim()}
            className="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold px-5 py-2.5 rounded-xl text-xs transition-colors flex items-center space-x-1 disabled:opacity-50"
          >
            <span>{loadingChat ? 'Thinking...' : 'Ask Copilot'}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </form>

        {chatResponse && (
          <div className="p-4 rounded-xl bg-blue-50/60 border border-blue-200 text-xs text-slate-800 leading-relaxed">
            <span className="font-bold text-blue-900 block mb-1">Copilot Operational Response:</span>
            {chatResponse}
          </div>
        )}
      </div>

      {/* Setup Guide for NVIDIA NIM Free API Key */}
      <div className="p-5 bg-slate-100 border border-slate-200 rounded-xl text-xs space-y-2">
        <div className="flex items-center space-x-2 font-bold text-slate-900">
          <KeyRound className="w-4 h-4 text-emerald-600" />
          <span>How to activate the Free NVIDIA NIM API Key (1,000 Free Credits)</span>
        </div>
        <ol className="list-decimal list-inside space-y-1 text-slate-600 pl-1">
          <li>Visit <a href="https://build.nvidia.com" target="_blank" rel="noreferrer" className="text-emerald-700 font-semibold hover:underline">build.nvidia.com</a> and sign in with any email.</li>
          <li>Navigate to <strong>API Catalog</strong> $\rightarrow$ Select <strong>Meta Llama 3.1 8B Instruct</strong> (or Llama 3.3 70B).</li>
          <li>Click <strong>Generate API Key</strong> (NVIDIA provides 1,000 free inference credits on signup).</li>
          <li>Paste your key into your project root <code className="bg-white px-1.5 py-0.5 rounded border border-slate-300 text-slate-900">.env</code> file:
            <pre className="mt-1 bg-slate-900 text-emerald-400 p-2 rounded-md font-mono text-[11px]">
              NVIDIA_API_KEY=nvapi-your-key-here
            </pre>
          </li>
          <li>Restart the backend (<code className="bg-white px-1.5 py-0.5 rounded border border-slate-300 text-slate-900">python run_backend.py</code>) to immediately enjoy live open-weights LLM inference!</li>
        </ol>
      </div>
    </div>
  );
}
