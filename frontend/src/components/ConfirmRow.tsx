import React, { useState } from 'react';
import { AISuggestionItem } from '../types/kyc';

interface ConfirmRowProps {
  suggestion: AISuggestionItem;
  onSelectCitation?: (doc: string, page: number, line: number, quote?: string) => void;
  onDecision: (
    suggestionId: number,
    payload: {
      action: 'accept' | 'edit' | 'reject';
      final_value: string;
      reason_code?: string;
      rationale?: string;
      time_spent_ms?: number;
      source_opened?: boolean;
    }
  ) => Promise<void>;
  disabled?: boolean;
}

export const ConfirmRow: React.FC<ConfirmRowProps> = ({
  suggestion,
  onSelectCitation,
  onDecision,
  disabled = false,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [isRejecting, setIsRejecting] = useState(false);
  const [editValue, setEditValue] = useState(suggestion.decision?.final_value ?? suggestion.value);
  const [reasonCode, setReasonCode] = useState<string>(suggestion.decision?.reason_code || 'wrong_value');
  const [rationale, setRationale] = useState<string>(suggestion.decision?.rationale || '');
  const [isPending, setIsPending] = useState(false);
  const [sourceOpened, setSourceOpened] = useState(false);

  const hasDecision = suggestion.has_decision && suggestion.decision;
  const currentAction = suggestion.decision?.action;

  const handleCitationClick = () => {
    if (suggestion.doc_source && suggestion.page && suggestion.line && onSelectCitation) {
      setSourceOpened(true);
      onSelectCitation(
        suggestion.doc_source,
        suggestion.page,
        suggestion.line,
        suggestion.verbatim_quote || undefined
      );
    }
  };

  const handleAccept = async () => {
    setIsPending(true);
    try {
      await onDecision(suggestion.id, {
        action: 'accept',
        final_value: suggestion.value,
        source_opened: sourceOpened,
      });
      setIsEditing(false);
      setIsRejecting(false);
    } finally {
      setIsPending(false);
    }
  };

  const handleSaveEdit = async () => {
    if (!editValue.trim()) return;
    setIsPending(true);
    try {
      await onDecision(suggestion.id, {
        action: 'edit',
        final_value: editValue,
        reason_code: reasonCode,
        rationale: rationale.trim() || undefined,
        source_opened: sourceOpened,
      });
      setIsEditing(false);
      setIsRejecting(false);
    } finally {
      setIsPending(false);
    }
  };

  const handleConfirmReject = async () => {
    setIsPending(true);
    try {
      await onDecision(suggestion.id, {
        action: 'reject',
        final_value: '',
        reason_code: reasonCode,
        rationale: rationale.trim() || undefined,
        source_opened: sourceOpened,
      });
      setIsEditing(false);
      setIsRejecting(false);
    } finally {
      setIsPending(false);
    }
  };

  const getTypeBadge = () => {
    switch (suggestion.field_type) {
      case 'EXTRACTED':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 border border-blue-200">
            EXTRACTED
          </span>
        );
      case 'COMPUTED':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800 border border-purple-200">
            COMPUTED
          </span>
        );
      case 'NOT_FOUND':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800 border border-amber-200">
            NOT_FOUND
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div
      className={`p-4 rounded-lg border transition-all ${
        hasDecision
          ? currentAction === 'accept'
            ? 'bg-emerald-50/50 border-emerald-200'
            : currentAction === 'edit'
            ? 'bg-amber-50/50 border-amber-200'
            : 'bg-rose-50/50 border-rose-200 opacity-80'
          : 'bg-white border-slate-200 hover:border-slate-300 shadow-sm'
      }`}
    >
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        {/* Left info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <span className="text-sm font-semibold text-slate-900">{suggestion.field_name}</span>
            {getTypeBadge()}
            {suggestion.citation_verified && (
              <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-emerald-100 text-emerald-800 border border-emerald-200">
                Verified Quote
              </span>
            )}
            {hasDecision && (
              <span
                className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold uppercase ${
                  currentAction === 'accept'
                    ? 'bg-emerald-600 text-white'
                    : currentAction === 'edit'
                    ? 'bg-amber-600 text-white'
                    : 'bg-rose-600 text-white'
                }`}
              >
                {currentAction}ed
              </span>
            )}
          </div>

          <div className="text-sm text-slate-800 font-medium">
            {hasDecision && currentAction === 'edit' ? (
              <div className="flex items-center gap-2">
                <span className="line-through text-slate-400">{suggestion.value}</span>
                <span className="text-amber-700 font-bold">{suggestion.decision?.final_value}</span>
              </div>
            ) : hasDecision && currentAction === 'reject' ? (
              <span className="line-through text-rose-500">{suggestion.value || '(No Value)'}</span>
            ) : (
              <span>{suggestion.value || '(None)'}</span>
            )}
          </div>

          {suggestion.formula && (
            <div className="mt-1 text-xs text-purple-700 font-mono bg-purple-50 px-2 py-1 rounded inline-block">
              Formula: {suggestion.formula}
            </div>
          )}

          {/* Citation snippet */}
          {suggestion.doc_source && suggestion.page && suggestion.line && (
            <div className="mt-2 flex items-center gap-2 text-xs flex-wrap">
              <button
                type="button"
                onClick={handleCitationClick}
                className="inline-flex items-center gap-1 font-mono text-blue-600 hover:text-blue-800 hover:underline bg-blue-50 px-2 py-0.5 rounded border border-blue-200 transition-colors"
                title="Click to view & highlight in PDF"
              >
                <span>Doc: {suggestion.doc_source} (P.{suggestion.page}, L.{suggestion.line})</span>
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </button>
              {suggestion.verbatim_quote && (
                <span className="text-slate-500 italic max-w-md truncate" title={suggestion.verbatim_quote}>
                  "{suggestion.verbatim_quote}"
                </span>
              )}
            </div>
          )}

          {/* Existing Decision Notes */}
          {hasDecision && (suggestion.decision?.reason_code || suggestion.decision?.rationale) && (
            <div className="mt-2 text-xs text-slate-600 bg-white/80 p-2 rounded border border-slate-200">
              {suggestion.decision.reason_code && (
                <span className="font-semibold text-slate-700 mr-2">
                  Reason: {suggestion.decision.reason_code}
                </span>
              )}
              {suggestion.decision.rationale && <span>Rationale: {suggestion.decision.rationale}</span>}
            </div>
          )}
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2 shrink-0">
          {!isEditing && !isRejecting ? (
            <>
              <button
                type="button"
                disabled={disabled || isPending}
                onClick={handleAccept}
                className={`px-3 py-1.5 rounded text-xs font-semibold transition-colors ${
                  hasDecision && currentAction === 'accept'
                    ? 'bg-emerald-600 text-white'
                    : 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-300'
                }`}
              >
                Accept
              </button>
              <button
                type="button"
                disabled={disabled || isPending}
                onClick={() => {
                  setIsEditing(true);
                  setIsRejecting(false);
                }}
                className={`px-3 py-1.5 rounded text-xs font-semibold transition-colors ${
                  hasDecision && currentAction === 'edit'
                    ? 'bg-amber-600 text-white'
                    : 'bg-amber-50 text-amber-700 hover:bg-amber-100 border border-amber-300'
                }`}
              >
                Edit
              </button>
              <button
                type="button"
                disabled={disabled || isPending}
                onClick={() => {
                  setIsRejecting(true);
                  setIsEditing(false);
                }}
                className={`px-3 py-1.5 rounded text-xs font-semibold transition-colors ${
                  hasDecision && currentAction === 'reject'
                    ? 'bg-rose-600 text-white'
                    : 'bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-300'
                }`}
              >
                Reject
              </button>
            </>
          ) : isEditing ? (
            <button
              type="button"
              onClick={() => setIsEditing(false)}
              className="text-xs text-slate-500 hover:text-slate-800"
            >
              Cancel
            </button>
          ) : (
            <button
              type="button"
              onClick={() => setIsRejecting(false)}
              className="text-xs text-slate-500 hover:text-slate-800"
            >
              Cancel
            </button>
          )}
        </div>
      </div>

      {/* Edit Form Drawer */}
      {isEditing && (
        <div className="mt-4 pt-3 border-t border-slate-200 space-y-3 bg-amber-50/70 p-3 rounded-md">
          <h4 className="text-xs font-semibold text-amber-900 uppercase tracking-wide">
            Edit Extracted Value
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">
                Correct Value <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
                className="w-full px-2.5 py-1.5 text-xs border border-slate-300 rounded focus:ring-1 focus:ring-amber-500 bg-white"
                placeholder="Enter corrected value..."
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">
                Reason Code <span className="text-rose-500">*</span>
              </label>
              <select
                value={reasonCode}
                onChange={(e) => setReasonCode(e.target.value)}
                className="w-full px-2.5 py-1.5 text-xs border border-slate-300 rounded focus:ring-1 focus:ring-amber-500 bg-white"
              >
                <option value="wrong_value">Wrong Value</option>
                <option value="wrong_source">Wrong Source / Citation</option>
                <option value="missed_party">Missed Party</option>
                <option value="stale_document">Stale Document</option>
                <option value="name_match_error">Name / Entity Resolution Error</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">
              Rationale / Notes
            </label>
            <input
              type="text"
              value={rationale}
              onChange={(e) => setRationale(e.target.value)}
              className="w-full px-2.5 py-1.5 text-xs border border-slate-300 rounded focus:ring-1 focus:ring-amber-500 bg-white"
              placeholder="e.g. Stock transfer sheet shows 60% transferred to Calder..."
            />
          </div>
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setIsEditing(false)}
              className="px-3 py-1 text-xs border border-slate-300 rounded text-slate-700 hover:bg-slate-100"
            >
              Cancel
            </button>
            <button
              type="button"
              disabled={isPending || !editValue.trim()}
              onClick={handleSaveEdit}
              className="px-3 py-1 text-xs bg-amber-600 hover:bg-amber-700 text-white rounded font-medium disabled:opacity-50"
            >
              {isPending ? 'Saving...' : 'Save Edit'}
            </button>
          </div>
        </div>
      )}

      {/* Reject Form Drawer */}
      {isRejecting && (
        <div className="mt-4 pt-3 border-t border-slate-200 space-y-3 bg-rose-50/70 p-3 rounded-md">
          <h4 className="text-xs font-semibold text-rose-900 uppercase tracking-wide">
            Reject AI Suggestion
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">
                Reason Code <span className="text-rose-500">*</span>
              </label>
              <select
                value={reasonCode}
                onChange={(e) => setReasonCode(e.target.value)}
                className="w-full px-2.5 py-1.5 text-xs border border-slate-300 rounded focus:ring-1 focus:ring-rose-500 bg-white"
              >
                <option value="wrong_value">Wrong Value</option>
                <option value="wrong_source">Wrong Source / Citation</option>
                <option value="missed_party">Missed Party</option>
                <option value="stale_document">Stale Document</option>
                <option value="name_match_error">Name / Entity Resolution Error</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">
                Rationale / Explanation
              </label>
              <input
                type="text"
                value={rationale}
                onChange={(e) => setRationale(e.target.value)}
                className="w-full px-2.5 py-1.5 text-xs border border-slate-300 rounded focus:ring-1 focus:ring-rose-500 bg-white"
                placeholder="Why is this suggestion invalid?"
              />
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setIsRejecting(false)}
              className="px-3 py-1 text-xs border border-slate-300 rounded text-slate-700 hover:bg-slate-100"
            >
              Cancel
            </button>
            <button
              type="button"
              disabled={isPending}
              onClick={handleConfirmReject}
              className="px-3 py-1 text-xs bg-rose-600 hover:bg-rose-700 text-white rounded font-medium disabled:opacity-50"
            >
              {isPending ? 'Rejecting...' : 'Confirm Rejection'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
