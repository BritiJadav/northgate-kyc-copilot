import React from 'react';
import { ShieldAlert, Zap, Clock } from 'lucide-react';

interface BannerProps {
  demoMode?: boolean;
  simulatedDate?: string;
}

export const Banner: React.FC<BannerProps> = ({ demoMode = true, simulatedDate = '2026-11-12' }) => {
  return (
    <div className="bg-slate-900 border-b border-slate-800 text-slate-200 text-xs py-1.5 px-4 flex flex-wrap items-center justify-between gap-2 shadow-inner">
      <div className="flex items-center space-x-2 font-medium">
        <span className="flex h-2 w-2 relative">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
        </span>
        <span className="tracking-wide text-slate-300 font-semibold uppercase">Northgate Financial Onboarding Copilot</span>
        <span className="text-slate-500">|</span>
        <span className="bg-amber-500/20 text-amber-300 border border-amber-500/40 px-2 py-0.5 rounded font-mono font-bold tracking-wider">
          SYNTHETIC DEMO DATA ONLY
        </span>
      </div>

      <div className="flex items-center space-x-4">
        {demoMode && (
          <span className="inline-flex items-center space-x-1 bg-blue-500/10 text-blue-300 border border-blue-500/30 px-2 py-0.5 rounded">
            <Zap className="w-3 h-3 text-blue-400" />
            <span>Resilient Demo Mode Active (C12)</span>
          </span>
        )}
        <span className="inline-flex items-center space-x-1.5 text-slate-300">
          <Clock className="w-3 h-3 text-slate-400" />
          <span>Simulated Clock: <strong className="font-mono text-white">{simulatedDate}</strong></span>
        </span>
      </div>
    </div>
  );
};
