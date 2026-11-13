import React, { useEffect, useState } from 'react';
import { governanceApi, EvalReportResponse } from '../api/governanceApi';

export const EvalPage: React.FC = () => {
  const [report, setReport] = useState<EvalReportResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchReport = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await governanceApi.getEvalReport();
      setReport(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to load evaluation report');
    } finally {
      setLoading(false);
    }
  };

  const handleRunEval = async () => {
    setRunning(true);
    setError(null);
    try {
      const data = await governanceApi.runEval();
      setReport(data);
    } catch (err: any) {
      setError(err?.message || 'Evaluation run failed');
    } finally {
      setRunning(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, []);

  if (loading && !report) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mb-3" />
        <p className="text-sm text-slate-600">Loading evaluation report from answer keys...</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              Evaluation Harness Report
            </h1>
            <span
              className={`inline-flex items-center px-2.5 py-0.5 rounded text-xs font-bold ${
                report?.overall_status === 'PASS'
                  ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                  : 'bg-rose-100 text-rose-800 border border-rose-300'
              }`}
            >
              OVERALL: {report?.overall_status}
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-600">
            Ground-truth regression evaluation across all 3 Document Chaser cases and all 5 Analyst Assist companies.
          </p>
        </div>

        <button
          onClick={handleRunEval}
          disabled={running}
          className="inline-flex items-center px-4 py-2 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm transition-colors disabled:opacity-50"
        >
          <svg
            className={`w-4 h-4 mr-1.5 ${running ? 'animate-spin' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {running ? 'Executing Evaluation...' : 'Re-Run Evaluation Harness'}
        </button>
      </div>

      {error && (
        <div className="bg-rose-50 border border-rose-200 text-rose-800 p-4 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
            Module A Gap F1
          </span>
          <div className="text-2xl font-black text-emerald-600 mt-1">
            {((report?.summary.module_a_gap_f1 || 0) * 100).toFixed(1)}%
          </div>
          <span className="text-[10px] text-slate-400">Target: &gt;= 95%</span>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
            Guardrail Accuracy
          </span>
          <div className="text-2xl font-black text-emerald-600 mt-1">
            {((report?.summary.module_a_guardrail_accuracy || 0) * 100).toFixed(1)}%
          </div>
          <span className="text-[10px] text-slate-400">5 adversarial tests</span>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
            Module B Companies
          </span>
          <div className="text-2xl font-black text-indigo-600 mt-1">
            {report?.summary.module_b_companies_passed} / {report?.summary.module_b_companies_total}
          </div>
          <span className="text-[10px] text-slate-400">100% ground truth match</span>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
            Kestrel Failure Modes
          </span>
          <div className="text-2xl font-black text-purple-600 mt-1">
            {report?.summary.kestrel_failure_modes_passed} / 3
          </div>
          <span className="text-[10px] text-slate-400">Berg, Nominee, Trustee</span>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
            Citation Verifier
          </span>
          <div className="text-2xl font-black text-emerald-600 mt-1">
            {((report?.summary.citation_verifier_accuracy || 0) * 100).toFixed(0)}%
          </div>
          <span className="text-[10px] text-slate-400">Deterministic verbatim gate</span>
        </div>
      </div>

      {/* Section 1: The 3 Kestrel Failure Modes */}
      <div className="bg-white rounded-xl border border-purple-200 shadow-sm overflow-hidden">
        <div className="p-6 bg-purple-50/60 border-b border-purple-200 flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-purple-950">
              Company E: 3 Complex Failure Mode Validations
            </h2>
            <p className="text-xs text-purple-700 mt-0.5">
              Specific stress tests proving the system avoids classic LLM failure patterns in multi-tier corporate hierarchies.
            </p>
          </div>
          <span className="text-xs font-mono font-bold text-purple-900 bg-purple-200/70 px-2.5 py-1 rounded">
            Kestrel Trading Ltd
          </span>
        </div>

        <div className="divide-y divide-purple-100">
          {report?.module_b.kestrel_failure_modes &&
            Object.entries(report.module_b.kestrel_failure_modes).map(([key, fm]: [string, any]) => (
              <div key={key} className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-purple-900">{fm.name}</span>
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold ${
                        fm.passed
                          ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                          : 'bg-rose-100 text-rose-800 border border-rose-300'
                      }`}
                    >
                      {fm.passed ? 'PASSED' : 'FAILED'}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600">{fm.details}</p>
                </div>
              </div>
            ))}
        </div>
      </div>

      {/* Section 2: Module A Gap Detection Precision & Recall Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-6 bg-slate-50 border-b border-slate-200">
          <h2 className="text-base font-bold text-slate-900">
            Module A: Gap Detection Precision, Recall & F1
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Single-pass gap discovery evaluated against ground truth requirements across all parties.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-100 text-slate-600 uppercase font-semibold border-b border-slate-200">
              <tr>
                <th className="px-4 py-3">Case</th>
                <th className="px-4 py-3">Client Name</th>
                <th className="px-4 py-3">Expected Gaps</th>
                <th className="px-4 py-3">Detected Gaps</th>
                <th className="px-4 py-3">True Positives</th>
                <th className="px-4 py-3">False Positives</th>
                <th className="px-4 py-3">False Negatives</th>
                <th className="px-4 py-3">Precision</th>
                <th className="px-4 py-3">Recall</th>
                <th className="px-4 py-3">F1 Score</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {report?.module_a.case_breakdown.map((c: any) => (
                <tr key={c.case_number} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-mono font-medium text-slate-800">{c.case_number}</td>
                  <td className="px-4 py-3 font-semibold text-slate-900">{c.client_name}</td>
                  <td className="px-4 py-3 text-slate-700">{c.expected_count}</td>
                  <td className="px-4 py-3 text-slate-700">{c.detected_count}</td>
                  <td className="px-4 py-3 text-emerald-700 font-bold">{c.true_positives}</td>
                  <td className="px-4 py-3 text-slate-400">{c.false_positives}</td>
                  <td className="px-4 py-3 text-slate-400">{c.false_negatives}</td>
                  <td className="px-4 py-3 font-mono">{(c.precision * 100).toFixed(1)}%</td>
                  <td className="px-4 py-3 font-mono">{(c.recall * 100).toFixed(1)}%</td>
                  <td className="px-4 py-3 font-mono font-bold text-indigo-700">{(c.f1 * 100).toFixed(1)}%</td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                      {c.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Section 3: Module B Company Breakdown */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-6 bg-slate-50 border-b border-slate-200">
          <h2 className="text-base font-bold text-slate-900">
            Module B: 5 Company Hierarchy Accuracy
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Validation of look-through calculation, voting shares, and OCR handling across all seeded corporate structures.
          </p>
        </div>

        <div className="divide-y divide-slate-200">
          {report?.module_b.company_breakdown.map((comp: any) => (
            <div key={comp.company} className="p-5 hover:bg-slate-50 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-slate-900">{comp.company}</span>
                  <span className="text-xs font-mono text-slate-500 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                    {comp.type}
                  </span>
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                    {comp.status}
                  </span>
                </div>
                {comp.metrics && (
                  <p className="text-xs text-slate-500 font-mono">
                    Metrics: {JSON.stringify(comp.metrics)}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
