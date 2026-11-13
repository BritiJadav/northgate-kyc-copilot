import React, { useState } from 'react';
import { PossibleMatchItem } from '../types/kyc';
import { UserCheck, Users, HelpCircle, CheckCircle2, XCircle } from 'lucide-react';

interface PossibleMatchCardProps {
  match: PossibleMatchItem;
  onResolve: (matchId: number, action: 'confirm_same' | 'confirm_different') => Promise<void>;
}

export const PossibleMatchCard: React.FC<PossibleMatchCardProps> = ({ match, onResolve }) => {
  const [resolving, setResolving] = useState(false);

  const handleResolve = async (action: 'confirm_same' | 'confirm_different') => {
    setResolving(true);
    try {
      await onResolve(match.id, action);
    } finally {
      setResolving(false);
    }
  };

  const isResolved = match.status !== 'pending';

  return (
    <div className={`rounded-lg border p-4 shadow-sm transition space-y-3 ${
      match.status === 'confirmed_same'
        ? 'bg-emerald-50/50 border-emerald-300'
        : match.status === 'confirmed_different'
        ? 'bg-slate-50 border-slate-300'
        : 'bg-amber-50/70 border-amber-300 ring-2 ring-amber-400/20'
    }`}>
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 rounded bg-amber-100 text-amber-800 border border-amber-300">
            <Users className="w-4 h-4" />
          </div>
          <div>
            <span className="text-[10px] uppercase font-mono font-bold text-amber-800 tracking-wider">
              Entity Resolution Candidate (Constraint C8)
            </span>
            <h4 className="text-sm font-bold text-slate-900 mt-0.5">
              Possible Match: Confirm or Separate?
            </h4>
          </div>
        </div>

        {isResolved ? (
          <span className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded text-xs font-semibold ${
            match.status === 'confirmed_same'
              ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
              : 'bg-slate-200 text-slate-800'
          }`}>
            {match.status === 'confirmed_same' ? (
              <>
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>Confirmed Same Person</span>
              </>
            ) : (
              <>
                <XCircle className="w-3.5 h-3.5 text-slate-600" />
                <span>Confirmed Separate Persons</span>
              </>
            )}
          </span>
        ) : (
          <span className="bg-amber-200 text-amber-900 text-[11px] font-bold px-2 py-0.5 rounded-full border border-amber-300 animate-pulse">
            Decision Required Before Submit
          </span>
        )}
      </div>

      {/* Comparison Details */}
      <div className="bg-white border border-slate-200 rounded p-3 text-xs space-y-2">
        <div className="grid grid-cols-2 gap-4">
          <div className="p-2 bg-slate-50 rounded border border-slate-100">
            <span className="text-[10px] text-slate-400 uppercase font-mono block">Person A</span>
            <strong className="text-slate-900 text-xs">{match.person_a_name}</strong>
            {match.person_a_dob && <div className="text-[11px] text-slate-600 mt-0.5">DOB: {match.person_a_dob}</div>}
          </div>
          <div className="p-2 bg-slate-50 rounded border border-slate-100">
            <span className="text-[10px] text-slate-400 uppercase font-mono block">Person B</span>
            <strong className="text-slate-900 text-xs">{match.person_b_name}</strong>
            {match.person_b_dob && <div className="text-[11px] text-slate-600 mt-0.5">DOB: {match.person_b_dob}</div>}
          </div>
        </div>

        <p className="text-[11px] text-slate-600 leading-relaxed pt-1">
          <strong>AI Finding:</strong> {match.reason}
        </p>

        <p className="text-[10px] text-slate-400 italic">
          * Per Northgate KYC Policy (Constraint C8), the AI never automatically merges individuals. Confirming 'Same Person' will trigger an immediate deterministic recalculation of look-through ownership.
        </p>
      </div>

      {/* Actions */}
      {!isResolved && (
        <div className="flex items-center justify-end space-x-2 pt-1">
          <button
            onClick={() => handleResolve('confirm_different')}
            disabled={resolving}
            className="px-3 py-1.5 rounded text-xs font-medium text-slate-700 bg-white border border-slate-300 hover:bg-slate-50 transition disabled:opacity-50"
          >
            Keep Separate
          </button>
          <button
            onClick={() => handleResolve('confirm_same')}
            disabled={resolving}
            className="px-3.5 py-1.5 rounded text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 shadow-sm transition disabled:opacity-50 flex items-center space-x-1.5"
          >
            <UserCheck className="w-3.5 h-3.5" />
            <span>Confirm Same Person (Recompute %)</span>
          </button>
        </div>
      )}
    </div>
  );
};
