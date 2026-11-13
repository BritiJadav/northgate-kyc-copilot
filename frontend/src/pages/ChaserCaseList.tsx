import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { NavLink } from 'react-router-dom';
import { chaseApi } from '../api/chaseApi';
import { FileSearch, Clock, ArrowRight, UserCheck, AlertCircle, RefreshCw } from 'lucide-react';

export const ChaserCaseList: React.FC = () => {
  const { data: cases, isLoading, error, refetch } = useQuery({
    queryKey: ['chaseCases'],
    queryFn: chaseApi.listCases,
  });

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-12 text-center text-slate-500">
        <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-600" />
        <span>Loading onboarding cases...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8 text-rose-600 text-sm">
        Failed to load cases: {(error as Error).message}
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
      {/* Page Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs uppercase font-mono font-bold text-blue-600 tracking-wider">Module A</span>
          <h1 className="text-2xl font-bold text-slate-900">Document Chaser: Onboarding Cases</h1>
          <p className="text-xs text-slate-500 mt-1">
            Single-pass gap detection eliminates multiple chase rounds. Relationship Manager reviews and sends.
          </p>
        </div>

        <button
          onClick={() => refetch()}
          className="inline-flex items-center space-x-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded px-3 py-1.5 hover:bg-slate-50 shadow-sm"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Cases Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <table className="min-w-full divide-y divide-slate-200 text-left text-xs">
          <thead className="bg-slate-50 text-slate-600 font-semibold uppercase tracking-wider text-[11px]">
            <tr>
              <th className="py-3 px-4">Case #</th>
              <th className="py-3 px-4">Client Name</th>
              <th className="py-3 px-4">Client Type</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Last Contact</th>
              <th className="py-3 px-4">Rounds</th>
              <th className="py-3 px-4">Active Gaps</th>
              <th className="py-3 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 bg-white">
            {cases?.map((c) => (
              <tr key={c.id} className="hover:bg-slate-50/70 transition">
                <td className="py-3.5 px-4 font-mono font-medium text-slate-600">
                  {c.case_number}
                </td>
                <td className="py-3.5 px-4 font-bold text-slate-900 text-sm">
                  {c.client_name}
                </td>
                <td className="py-3.5 px-4 capitalize text-slate-700">
                  <span className="bg-slate-100 px-2 py-0.5 rounded text-[11px] font-medium text-slate-700 border border-slate-200">
                    {c.client_type}
                  </span>
                </td>
                <td className="py-3.5 px-4">
                  <span
                    className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold ${
                      c.status === 'awaiting_docs'
                        ? 'bg-blue-50 text-blue-800 border border-blue-200'
                        : c.status === 'stalled'
                        ? 'bg-rose-50 text-rose-800 border border-rose-200'
                        : 'bg-amber-50 text-amber-800 border border-amber-200'
                    }`}
                  >
                    {c.status.replace(/_/g, ' ')}
                  </span>
                </td>
                <td className="py-3.5 px-4 text-slate-600 font-mono text-[11px]">
                  {c.last_contact_date || 'Not yet contacted'}
                </td>
                <td className="py-3.5 px-4 font-mono text-slate-700">
                  Round {c.rounds_count}
                </td>
                <td className="py-3.5 px-4">
                  <span className="bg-rose-50 text-rose-700 border border-rose-200 text-xs font-semibold px-2 py-0.5 rounded-full">
                    {c.gap_count} gaps
                  </span>
                </td>
                <td className="py-3.5 px-4 text-right">
                  <NavLink
                    to={`/chaser/${c.id}`}
                    className="inline-flex items-center space-x-1 font-semibold text-xs text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded transition border border-blue-200"
                  >
                    <span>Open Case</span>
                    <ArrowRight className="w-3 h-3" />
                  </NavLink>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
