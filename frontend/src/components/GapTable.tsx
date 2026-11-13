import React, { useState } from 'react';
import { GapRow, GapStatus } from '../types';
import { AlertCircle, CheckCircle2, Clock, Plus, Trash2, Undo2, HelpCircle } from 'lucide-react';

interface GapTableProps {
  gaps: GapRow[];
  onToggleGap: (gapId: number, isActive: boolean, reason?: string) => Promise<void>;
  onAddGap: (payload: { party_name: string; requirement: string; notes?: string }) => Promise<void>;
  parties: Array<{ name: string; role: string }>;
}

export const GapTable: React.FC<GapTableProps> = ({ gaps, onToggleGap, onAddGap, parties }) => {
  const [showAddModal, setShowAddModal] = useState(false);
  const [newParty, setNewParty] = useState(parties[0]?.name || '');
  const [newReq, setNewReq] = useState('');
  const [newNotes, setNewNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const getStatusBadge = (status: GapStatus) => {
    switch (status) {
      case 'OK':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
            <CheckCircle2 className="w-3 h-3 mr-1 text-emerald-600" /> OK
          </span>
        );
      case 'MISSING':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-rose-100 text-rose-800 border border-rose-200">
            <AlertCircle className="w-3 h-3 mr-1 text-rose-600" /> MISSING
          </span>
        );
      case 'EXPIRED':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-amber-100 text-amber-900 border border-amber-300">
            <Clock className="w-3 h-3 mr-1 text-amber-700" /> EXPIRED
          </span>
        );
      case 'STALE':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200">
            <Clock className="w-3 h-3 mr-1 text-amber-600" /> STALE (&gt;3m)
          </span>
        );
      case 'INCOMPLETE':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-indigo-50 text-indigo-800 border border-indigo-200">
            <HelpCircle className="w-3 h-3 mr-1 text-indigo-600" /> INCOMPLETE
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-slate-100 text-slate-800 border border-slate-200">
            {status}
          </span>
        );
    }
  };

  const handleCreateGap = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newReq.trim()) return;
    setIsSubmitting(true);
    try {
      await onAddGap({
        party_name: newParty || parties[0]?.name || 'Client',
        requirement: newReq.trim(),
        notes: newNotes.trim() || undefined,
      });
      setNewReq('');
      setNewNotes('');
      setShowAddModal(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  const activeCount = gaps.filter(g => g.is_active && g.status !== 'OK').length;

  return (
    <div className="bg-white rounded-lg border border-slate-200 shadow-sm flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/50">
        <div>
          <h3 className="font-semibold text-slate-900 text-sm flex items-center space-x-2">
            <span>Deterministic Gap Matrix</span>
            <span className="bg-blue-100 text-blue-800 text-xs font-mono font-medium px-2 py-0.5 rounded-full">
              {activeCount} active gaps
            </span>
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Single-pass analysis across all identified parties. Evaluated via rule engine.
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="inline-flex items-center space-x-1 text-xs font-medium bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 rounded px-2.5 py-1.5 shadow-sm transition"
        >
          <Plus className="w-3.5 h-3.5 text-blue-600" />
          <span>Add Requirement</span>
        </button>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-x-auto overflow-y-auto">
        <table className="min-w-full divide-y divide-slate-200 text-left text-xs">
          <thead className="bg-slate-50 sticky top-0 z-10 text-slate-600 font-semibold uppercase tracking-wider text-[11px]">
            <tr>
              <th className="py-2.5 px-3">Party</th>
              <th className="py-2.5 px-3">Requirement</th>
              <th className="py-2.5 px-3">Status</th>
              <th className="py-2.5 px-3">Evidence / Reason</th>
              <th className="py-2.5 px-3">Rule ID</th>
              <th className="py-2.5 px-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 bg-white">
            {gaps.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center py-8 text-slate-400">
                  No gaps identified. Run analysis to evaluate requirements.
                </td>
              </tr>
            ) : (
              gaps.map((gap) => (
                <tr
                  key={gap.id}
                  className={`transition ${!gap.is_active ? 'opacity-40 bg-slate-50' : 'hover:bg-slate-50/60'}`}
                >
                  <td className="py-2.5 px-3 font-medium text-slate-900 whitespace-nowrap">
                    {gap.party_name}
                  </td>
                  <td className="py-2.5 px-3 font-medium text-slate-800">
                    {gap.requirement}
                  </td>
                  <td className="py-2.5 px-3 whitespace-nowrap">
                    {getStatusBadge(gap.status)}
                  </td>
                  <td className="py-2.5 px-3 text-slate-600 max-w-xs text-xs">
                    {gap.evidence || '—'}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-[11px] text-slate-500 whitespace-nowrap">
                    {gap.rule_id}
                  </td>
                  <td className="py-2.5 px-3 text-right whitespace-nowrap">
                    {gap.status !== 'OK' && (
                      gap.is_active ? (
                        <button
                          onClick={() => onToggleGap(gap.id, false, "Removed by RM during pre-send review")}
                          className="text-slate-400 hover:text-rose-600 p-1 rounded transition"
                          title="Exclude this gap from client chase email"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      ) : (
                        <button
                          onClick={() => onToggleGap(gap.id, true, "Restored by RM")}
                          className="text-blue-600 hover:text-blue-800 p-1 rounded transition flex items-center space-x-1 ml-auto text-xs"
                          title="Restore this gap into email draft"
                        >
                          <Undo2 className="w-3.5 h-3.5" />
                          <span>Restore</span>
                        </button>
                      )
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl border border-slate-200 max-w-md w-full p-5">
            <h4 className="font-semibold text-slate-900 text-sm">Add Document Requirement (RM Override)</h4>
            <p className="text-xs text-slate-500 mt-1">
              Add a specialized document requirement for this client. Logged in audit trail.
            </p>

            <form onSubmit={handleCreateGap} className="mt-4 space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-700">Target Party</label>
                <select
                  value={newParty}
                  onChange={(e) => setNewParty(e.target.value)}
                  className="mt-1 block w-full text-xs rounded border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"
                >
                  {parties.map((p) => (
                    <option key={p.name} value={p.name}>
                      {p.name} ({p.role})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700">Requirement Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Certified Power of Attorney, Tax Residency Certificate"
                  value={newReq}
                  onChange={(e) => setNewReq(e.target.value)}
                  className="mt-1 block w-full text-xs rounded border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700">Notes / Reason</label>
                <textarea
                  rows={2}
                  placeholder="Specific instructions or rationale for requesting this document"
                  value={newNotes}
                  onChange={(e) => setNewNotes(e.target.value)}
                  className="mt-1 block w-full text-xs rounded border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"
                />
              </div>

              <div className="mt-4 flex justify-end space-x-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-100 rounded"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-3 py-1.5 text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white rounded shadow-sm disabled:opacity-50"
                >
                  {isSubmitting ? 'Adding...' : 'Add Requirement'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
