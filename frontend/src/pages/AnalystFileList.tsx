import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { kycApi } from '../api/kycApi';
import { CompanySummary } from '../types/kyc';

export const AnalystFileList: React.FC = () => {
  const [files, setFiles] = useState<CompanySummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchFiles = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await kycApi.listFiles();
      setFiles(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to load company files');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'submitted':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300">
            Confirmed & Submitted
          </span>
        );
      case 'in_review':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-300">
            In Review
          </span>
        );
      case 'extracted':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-100 text-purple-800 border border-purple-300">
            AI Extracted
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-300">
            Pending Review
          </span>
        );
    }
  };

  const getCompanyDescription = (code: string) => {
    switch (code) {
      case 'ALDER_FINCH':
        return 'Company A: Clean single-tier warm-up (UK company, 2 natural person shareholders).';
      case 'BRIGHTWAVE':
        return 'Company B: Dual-class voting share discrepancy (ordinary shares vs non-voting preference).';
      case 'CALDER':
        return 'Company C: Low-legibility skewed scan transfer sheet requiring OCR / image inspection.';
      case 'ROWAN':
        return 'Company D: Discretionary trust structure with cyclic parent-subsidiary cross-holding.';
      case 'KESTREL':
        return 'Company E: Complex 4-tier chain, candidate Berg match (splits into 33.6%), nominee arrangement.';
      default:
        return 'KYC corporate entity file.';
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              Module B: Analyst Assist
            </h1>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
              11 of 62 Onboarding Days
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-600">
            Multi-tier incorporation review. AI pre-fills owners, percentages, voting control, and look-through with exact line citations.
          </p>
        </div>

        <button
          onClick={fetchFiles}
          disabled={loading}
          className="inline-flex items-center px-3 py-2 text-xs font-medium rounded border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 shadow-sm transition-colors"
        >
          <svg className={`w-3.5 h-3.5 mr-1.5 ${loading ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh Files
        </button>
      </div>

      {/* Philosophy Banner */}
      <div className="bg-gradient-to-r from-slate-900 to-indigo-950 text-white rounded-xl p-5 shadow-sm border border-slate-800">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="space-y-1">
            <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400">
              Governance & Verification Red Line
            </span>
            <p className="text-sm font-medium text-slate-100">
              "AI prepares, human decides." The system never outputs risk ratings and never auto-accepts look-through conclusions.
            </p>
            <p className="text-xs text-slate-300">
              Every row must be verified with document page and line citations. Citations are verified deterministically before display.
            </p>
          </div>
          <div className="flex items-center gap-3 text-xs bg-white/10 px-3 py-2 rounded-lg border border-white/15">
            <div>
              <span className="text-slate-300 block">Strict Data Separation:</span>
              <span className="text-emerald-400 font-bold font-mono">confirmed_records</span> only
            </div>
          </div>
        </div>
      </div>

      {/* Error display */}
      {error && (
        <div className="bg-rose-50 border border-rose-200 text-rose-800 p-4 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* File List */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
            Seeded KYC Corporate Files ({files.length})
          </h2>
          <span className="text-xs text-slate-500">
            Click 'Review File' to open the split citation and confirmation workspace
          </span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-slate-500 text-sm">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mb-3" />
            <p>Loading KYC files...</p>
          </div>
        ) : files.length === 0 ? (
          <div className="p-12 text-center text-slate-500 text-sm">
            No KYC files found. Please ensure seed data is initialized.
          </div>
        ) : (
          <div className="divide-y divide-slate-200">
            {files.map((file) => (
              <div
                key={file.id}
                className="p-6 hover:bg-slate-50/70 transition-colors flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center gap-3 flex-wrap">
                    <span className="font-mono text-xs font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200">
                      {file.code}
                    </span>
                    <h3 className="text-base font-semibold text-slate-900">
                      {file.name}
                    </h3>
                    {getStatusBadge(file.status)}
                    {file.pending_decisions_count > 0 ? (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800 border border-amber-300">
                        {file.pending_decisions_count} pending decision{file.pending_decisions_count === 1 ? '' : 's'}
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-600">
                        0 pending decisions
                      </span>
                    )}
                  </div>

                  <p className="text-xs text-slate-600">
                    {getCompanyDescription(file.code)}
                  </p>

                  <div className="flex items-center gap-4 text-xs text-slate-500 flex-wrap">
                    <span>
                      <strong className="text-slate-700">Jurisdiction:</strong> {file.jurisdiction}
                    </span>
                    <span>•</span>
                    <span>
                      <strong className="text-slate-700">Reg #:</strong> {file.registration_number}
                    </span>
                    {file.incorporation_date && (
                      <>
                        <span>•</span>
                        <span>
                          <strong className="text-slate-700">Incorp:</strong> {file.incorporation_date}
                        </span>
                      </>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                  <Link
                    to={`/analyst/${file.id}`}
                    className="inline-flex items-center px-4 py-2 rounded-lg text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 shadow-sm transition-colors"
                  >
                    <span>Open Split Review</span>
                    <svg className="w-4 h-4 ml-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                    </svg>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
