import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  governanceApi,
  GovernanceChecklistResponse,
  PilotModeResponse,
  ConfirmedRecordItem,
} from '../api/governanceApi';

export const GovernancePage: React.FC = () => {
  const [checklist, setChecklist] = useState<GovernanceChecklistResponse | null>(null);
  const [pilotMode, setPilotMode] = useState<PilotModeResponse | null>(null);
  const [records, setRecords] = useState<ConfirmedRecordItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [isUpdatingMode, setIsUpdatingMode] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [chk, mode, recs] = await Promise.all([
        governanceApi.getChecklist(),
        governanceApi.getMode(),
        governanceApi.getConfirmedRecords(),
      ]);
      setChecklist(chk);
      setPilotMode(mode);
      setRecords(recs);
    } catch (err: any) {
      setError(err?.message || 'Failed to load governance data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleToggleMode = async () => {
    if (!pilotMode) return;
    const newMode = pilotMode.pilot_mode === 'assisted' ? 'shadow' : 'assisted';
    setIsUpdatingMode(true);
    try {
      await governanceApi.updateMode(newMode);
      await loadData();
    } catch (err: any) {
      alert(`Failed to switch mode: ${err?.message || err}`);
    } finally {
      setIsUpdatingMode(false);
    }
  };

  const handleExport = (format: 'csv' | 'json') => {
    window.open(`/api/governance/export?format=${format}`, '_blank');
  };

  if (loading && !checklist) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mb-3" />
        <p className="text-sm text-slate-600">Checking system tripwires and auditor controls...</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Governance, Controls & Auditor Ledger
          </h1>
          <p className="mt-1 text-sm text-slate-600">
            Real-time verification of MLRO red lines, hard architectural constraints, and auditor-ready confirmed records.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/eval"
            className="inline-flex items-center px-3 py-2 text-xs font-semibold rounded-lg bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border border-indigo-300 shadow-sm transition-colors"
          >
            <svg className="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            View Eval Harness Report
          </Link>
          <button
            onClick={loadData}
            className="inline-flex items-center px-3 py-2 text-xs font-semibold rounded-lg border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 shadow-sm transition-colors"
          >
            <svg className="w-3.5 h-3.5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Re-run Tripwires
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-rose-50 border border-rose-200 text-rose-800 p-4 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* Pilot Mode Control Card */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-5">
        <div className="space-y-1.5 max-w-2xl">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Pilot Operating Mode
            </span>
            <span
              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold uppercase ${
                pilotMode?.pilot_mode === 'assisted'
                  ? 'bg-indigo-100 text-indigo-800 border border-indigo-300'
                  : 'bg-slate-200 text-slate-800 border border-slate-300'
              }`}
            >
              {pilotMode?.pilot_mode} Mode Active
            </span>
          </div>
          <p className="text-sm font-semibold text-slate-900">
            {pilotMode?.description}
          </p>
          <p className="text-xs text-slate-500">
            {pilotMode?.pilot_mode === 'assisted'
              ? 'Seeded canaries (10% rate) are injected into suggestions to verify analyst vigilance.'
              : 'Zero analyst exposure. Telemetry is collected in shadow logs for benchmark calibration.'}
          </p>
        </div>

        <button
          onClick={handleToggleMode}
          disabled={isUpdatingMode}
          className={`px-4 py-2 rounded-lg text-xs font-semibold shadow-sm transition-colors ${
            pilotMode?.pilot_mode === 'assisted'
              ? 'bg-slate-800 hover:bg-slate-900 text-white'
              : 'bg-indigo-600 hover:bg-indigo-700 text-white'
          }`}
        >
          {isUpdatingMode
            ? 'Updating...'
            : pilotMode?.pilot_mode === 'assisted'
            ? 'Switch to Shadow Mode'
            : 'Switch to Assisted Pilot Mode'}
        </button>
      </div>

      {/* 12 Hard Constraints Tripwire Checklist */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden space-y-0">
        <div className="p-6 bg-slate-50 border-b border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5">
              <span className="w-3 h-3 rounded-full bg-emerald-500" />
              <h2 className="text-base font-bold text-slate-900">
                12 Hard Non-Negotiable Constraints (C1 &ndash; C12)
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Automated tripwires run live on every request. Any constraint violation halts deployment.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
              {checklist?.passed_controls} of {checklist?.total_controls} Controls Verified PASS
            </span>
          </div>
        </div>

        <div className="divide-y divide-slate-200">
          {checklist?.checks.map((chk) => (
            <div key={chk.id} className="p-5 hover:bg-slate-50/60 transition-colors flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="space-y-1 flex-1">
                <div className="flex items-center gap-2.5 flex-wrap">
                  <span className="font-mono text-xs font-bold text-slate-700 bg-slate-100 px-2 py-0.5 rounded border border-slate-300">
                    {chk.id}
                  </span>
                  <span className="text-sm font-semibold text-slate-900">
                    {chk.name}
                  </span>
                  <span
                    className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold ${
                      chk.status === 'PASS'
                        ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                        : 'bg-rose-100 text-rose-800 border border-rose-200'
                    }`}
                  >
                    {chk.status}
                  </span>
                </div>
                <p className="text-xs text-slate-600">
                  {chk.description}
                </p>
                <p className="text-xs text-slate-400 font-mono">
                  Tripwire telemetry: {chk.details}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Confirmed Records Ledger (C9 Governance) */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden space-y-0">
        <div className="p-6 bg-slate-50 border-b border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5">
              <span className="w-3 h-3 rounded-full bg-indigo-600" />
              <h2 className="text-base font-bold text-slate-900">
                Downstream Confirmed Records Ledger ({records.length})
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Constraint C9: Downstream banking and audit consumers read exclusively from this ledger. AI suggestions table is strictly isolated.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => handleExport('csv')}
              className="inline-flex items-center px-3 py-1.5 text-xs font-semibold rounded-lg bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 shadow-sm transition-colors"
            >
              <svg className="w-3.5 h-3.5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Export CSV
            </button>
            <button
              onClick={() => handleExport('json')}
              className="inline-flex items-center px-3 py-1.5 text-xs font-semibold rounded-lg bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 shadow-sm transition-colors"
            >
              <svg className="w-3.5 h-3.5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Export JSON
            </button>
          </div>
        </div>

        {records.length === 0 ? (
          <div className="p-12 text-center text-slate-500 text-sm">
            <p>No confirmed records submitted yet.</p>
            <p className="text-xs text-slate-400 mt-1">
              Records appear here after an analyst verifies all fields in a KYC file and clicks 'Submit Confirmed KYC File'.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-100 text-slate-600 uppercase font-semibold border-b border-slate-200">
                <tr>
                  <th className="px-4 py-3">Company</th>
                  <th className="px-4 py-3">Field Name</th>
                  <th className="px-4 py-3">Confirmed Value</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Formula / Citation</th>
                  <th className="px-4 py-3">Confirmed By</th>
                  <th className="px-4 py-3">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {records.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50/80">
                    <td className="px-4 py-3 font-mono font-medium text-slate-800">
                      {r.company_code}
                    </td>
                    <td className="px-4 py-3 font-semibold text-slate-900">
                      {r.field_name}
                    </td>
                    <td className="px-4 py-3 font-medium text-emerald-700">
                      {r.value}
                    </td>
                    <td className="px-4 py-3">
                      <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-700 border border-slate-200 font-mono">
                        {r.field_type}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-500 max-w-xs truncate" title={r.formula || r.source_citation || ''}>
                      {r.formula || r.source_citation || '-'}
                    </td>
                    <td className="px-4 py-3 font-mono text-slate-600">
                      {r.confirmed_by}
                    </td>
                    <td className="px-4 py-3 text-slate-400 font-mono">
                      {r.created_at ? new Date(r.created_at).toLocaleString() : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
