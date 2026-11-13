import React from 'react';
import { NavLink } from 'react-router-dom';
import { FileSearch, Users, ArrowRight, ShieldCheck, Clock, CheckCircle2, AlertTriangle, Cpu } from 'lucide-react';

export const Home: React.FC = () => {
  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      {/* Hero / Context */}
      <div className="bg-white rounded-xl border border-slate-200 p-8 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="max-w-2xl space-y-3">
            <span className="text-xs uppercase font-mono font-bold tracking-widest text-blue-600 bg-blue-50 px-2.5 py-1 rounded border border-blue-200">
              Forward Deployed Engineer (FDE) Demo
            </span>
            <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
              Northgate KYC Copilot
            </h1>
            <p className="text-slate-600 text-sm leading-relaxed">
              At Northgate Financial, client KYC onboarding takes <strong>62 days per case</strong>.
              This platform targets the two primary human bottlenecks using an applied-AI architecture where
              <strong> "AI prepares, human decides"</strong>: nothing is ever auto-sent, and nothing is ever auto-accepted.
            </p>
          </div>

          <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-2 text-xs shrink-0 max-w-xs">
            <div className="font-semibold text-slate-800 uppercase tracking-wider text-[11px]">Core Architecture Rules</div>
            <div className="flex items-center space-x-2 text-slate-600">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>Simulated Outbox Only (C2)</span>
            </div>
            <div className="flex items-center space-x-2 text-slate-600">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>Zero Risk Scoring/Ratings (C4)</span>
            </div>
            <div className="flex items-center space-x-2 text-slate-600">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>Deterministic Citations & Math (C5, C6)</span>
            </div>
            <div className="flex items-center space-x-2 text-slate-600">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>Human Entity Resolution (C8)</span>
            </div>
          </div>
        </div>

        {/* 62-Day Bottleneck Split Visual Bar */}
        <div className="mt-8 pt-6 border-t border-slate-100">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-700 mb-2">
            <span>The 62-Day Onboarding Timeline Split</span>
            <span className="font-mono text-slate-500">62 Days Total</span>
          </div>

          <div className="h-9 w-full rounded-lg overflow-hidden flex shadow-inner text-xs font-semibold">
            {/* Module A */}
            <div
              className="bg-blue-600 text-white flex items-center justify-center px-2 transition hover:bg-blue-700"
              style={{ width: '27.4%' }}
              title="17 Days: Document Chaser (Module A)"
            >
              <span className="truncate">Module A: Chaser (17d)</span>
            </div>
            {/* Module B */}
            <div
              className="bg-indigo-600 text-white flex items-center justify-center px-2 transition hover:bg-indigo-700"
              style={{ width: '17.7%' }}
              title="11 Days: Analyst Assist (Module B)"
            >
              <span className="truncate">Module B: Analyst (11d)</span>
            </div>
            {/* Other */}
            <div
              className="bg-slate-200 text-slate-700 flex items-center justify-center px-2"
              style={{ width: '54.9%' }}
              title="34 Days: Operations & Account Setup"
            >
              <span className="truncate">Other Operations & Setup (34d)</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-3 text-xs text-slate-500">
            <div className="flex items-center space-x-1.5">
              <div className="w-3 h-3 rounded-sm bg-blue-600" />
              <span><strong>Module A (17 of 62 days):</strong> Missing docs found one at a time over 3 rounds.</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <div className="w-3 h-3 rounded-sm bg-indigo-600" />
              <span><strong>Module B (11 of 62 days):</strong> Reading complex multi-tier incorporation records.</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <div className="w-3 h-3 rounded-sm bg-slate-300" />
              <span><strong>Other Steps (34 days):</strong> Custody, credit lines & funding.</span>
            </div>
          </div>
        </div>
      </div>

      {/* Two Modules Launchpad */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Module A Card */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm hover:border-blue-300 transition flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-lg bg-blue-50 text-blue-600 border border-blue-200">
                <FileSearch className="w-6 h-6" />
              </div>
              <div>
                <span className="text-[11px] font-mono text-blue-600 uppercase font-bold tracking-wider">Module A</span>
                <h3 className="text-lg font-bold text-slate-900">Document Chaser</h3>
              </div>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed">
              Find <strong>EVERY document gap at once</strong> across all parties in a single deterministic pass.
              Auto-draft one consolidated email with RM placeholders. Pre-send guardrails catch forbidden phrases and
              confidential notes. Automatically triggers Day 3/6/9 reminder tasks via mock clock.
            </p>

            <div className="bg-slate-50 rounded-lg p-3 text-xs space-y-1.5 text-slate-700">
              <div className="font-semibold text-slate-800 text-[11px] uppercase">Seeded Test Cases:</div>
              <div>• <strong>Priya Raman:</strong> Expired passport + stale utility bill + missing SOF.</div>
              <div>• <strong>Harbourline Logistics:</strong> Missing register, pages 1-2 of 4 bank stmt, 2 UBOs.</div>
              <div>• <strong>Okafor Trust:</strong> Deed missing page 12 execution, Day 3 reminder fires.</div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
            <span className="text-xs text-slate-500 font-medium">3 Onboarding Cases</span>
            <NavLink
              to="/chaser"
              className="inline-flex items-center space-x-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-4 py-2 rounded-lg shadow-sm transition"
            >
              <span>Launch Document Chaser</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </NavLink>
          </div>
        </div>

        {/* Module B Card */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm hover:border-indigo-300 transition flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-lg bg-indigo-50 text-indigo-600 border border-indigo-200">
                <Users className="w-6 h-6" />
              </div>
              <div>
                <span className="text-[11px] font-mono text-indigo-600 uppercase font-bold tracking-wider">Module B</span>
                <h3 className="text-lg font-bold text-slate-900">Analyst Assist</h3>
              </div>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed">
              Pre-fills owners, shareholdings, and voting control with <strong>verifiable line citations</strong>.
              Deterministic Python look-through graph engine computes multi-path ownership. Detects same-person variants
              without auto-merging. Enforces no accept-all and strict data separation.
            </p>

            <div className="bg-slate-50 rounded-lg p-3 text-xs space-y-1.5 text-slate-700">
              <div className="font-semibold text-slate-800 text-[11px] uppercase">Seeded Companies & Keys:</div>
              <div>• <strong>Brightwave:</strong> Dual share classes $\implies$ Lumen holds 83.3% votes with 33.3% shares.</div>
              <div>• <strong>Calder Marine:</strong> Skewed scan of 2025 stock transfer updates 2023 truth.</div>
              <div>• <strong>Rowan Bay:</strong> Formation memorandum only $\implies$ NOT_FOUND current owners.</div>
              <div>• <strong>Kestrel:</strong> Tomas/Thomas Berg resolves to 33.6% UBO + 37% unresolved.</div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
            <span className="text-xs text-slate-500 font-medium">5 Corporate Files</span>
            <NavLink
              to="/analyst"
              className="inline-flex items-center space-x-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold px-4 py-2 rounded-lg shadow-sm transition"
            >
              <span>Launch Analyst Assist</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </NavLink>
          </div>
        </div>
      </div>
    </div>
  );
};
