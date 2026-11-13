import React from 'react';
import { GraphNode, GraphEdge } from '../types/kyc';
import { Network, Building2, User, ArrowRight, ShieldCheck, AlertCircle } from 'lucide-react';

interface OwnershipGraphProps {
  nodes?: GraphNode[];
  edges?: GraphEdge[];
  unresolvedPct?: number;
  companyName: string;
}

export const OwnershipGraph: React.FC<OwnershipGraphProps> = ({
  nodes = [],
  edges = [],
  unresolvedPct = 0,
  companyName,
}) => {
  return (
    <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-xs text-slate-900 flex items-center space-x-1.5 uppercase tracking-wider">
          <Network className="w-3.5 h-3.5 text-indigo-600" />
          <span>Look-Through Ownership Graph (Deterministic C6)</span>
        </h3>
        {unresolvedPct > 0 && (
          <span className="bg-amber-100 text-amber-900 text-xs font-semibold px-2.5 py-0.5 rounded border border-amber-300">
            {unresolvedPct}% Unresolved Holdings
          </span>
        )}
      </div>

      {/* Graph Visual Cards */}
      <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 overflow-x-auto">
        <div className="min-w-[600px] flex flex-col space-y-4">
          {/* Target Company Header */}
          <div className="bg-indigo-900 text-white rounded-lg p-3 flex items-center justify-between shadow-sm">
            <div className="flex items-center space-x-2">
              <Building2 className="w-5 h-5 text-indigo-300" />
              <div>
                <span className="text-[10px] uppercase font-mono text-indigo-300 block">Target Onboarding Entity</span>
                <span className="font-bold text-sm">{companyName}</span>
              </div>
            </div>
            <span className="bg-indigo-800 text-indigo-200 text-xs px-2.5 py-1 rounded font-mono font-medium">
              100.0% Issued Capital
            </span>
          </div>

          {/* Holdings Flow Tree */}
          <div className="space-y-2">
            <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
              Holding Paths & Ownership Edges ({edges.length} connections):
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {edges.map((edge, i) => (
                <div
                  key={i}
                  className="bg-white border border-slate-200 rounded p-2.5 flex items-center justify-between text-xs shadow-2xs hover:border-indigo-300 transition"
                >
                  <div className="flex items-center space-x-2 truncate">
                    {edge.source.toLowerCase().includes('ltd') ||
                    edge.source.toLowerCase().includes('b.v.') ||
                    edge.source.toLowerCase().includes('s.a.') ||
                    edge.source.toLowerCase().includes('lp') ? (
                      <Building2 className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                    ) : (
                      <User className="w-3.5 h-3.5 text-indigo-600 shrink-0" />
                    )}
                    <span className="font-medium text-slate-800 truncate" title={edge.source}>
                      {edge.source}
                    </span>
                  </div>

                  <div className="flex items-center space-x-2 shrink-0">
                    <span className="font-mono font-bold text-indigo-700 bg-indigo-50 border border-indigo-200 px-2 py-0.5 rounded text-[11px]">
                      {edge.percentage.toFixed(1)}%
                    </span>
                    <ArrowRight className="w-3 h-3 text-slate-400" />
                    <span className="text-slate-600 text-[11px] truncate max-w-[100px]" title={edge.target}>
                      {edge.target}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
