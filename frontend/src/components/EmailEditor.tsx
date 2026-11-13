import React, { useState, useEffect } from 'react';
import { ChaseEmail, GuardrailReport } from '../types';
import {
  Send,
  ShieldCheck,
  AlertTriangle,
  FileEdit,
  Sparkles,
  Info,
  CheckCircle2,
  XCircle,
  Eye,
  Lock
} from 'lucide-react';

interface EmailEditorProps {
  email?: ChaseEmail | null;
  possibleFollowons?: string | null;
  onSendSimulated: (subject: string, body: string) => Promise<void>;
  onReDraft: () => Promise<void>;
  isSending: boolean;
}

export const EmailEditor: React.FC<EmailEditorProps> = ({
  email,
  possibleFollowons,
  onSendSimulated,
  onReDraft,
  isSending,
}) => {
  const [subject, setSubject] = useState(email?.subject || '');
  const [body, setBody] = useState(email?.body || '');
  const [isEditing, setIsEditing] = useState(false);
  const [guardrailReport, setGuardrailReport] = useState<GuardrailReport | null>(null);

  useEffect(() => {
    if (email) {
      setSubject(email.subject);
      setBody(email.body);
      if (email.guardrail_report) {
        try {
          const parsed = typeof email.guardrail_report === 'string' ? JSON.parse(email.guardrail_report) : email.guardrail_report;
          setGuardrailReport(parsed);
        } catch {
          setGuardrailReport(null);
        }
      }
    }
  }, [email]);

  // Check for unresolved placeholders in real-time
  const placeholderRegex = /\[RM TO CONFIRM:\s*([^\]]+)\]/gi;
  const placeholderMatches = body.match(placeholderRegex) || [];
  const hasPlaceholders = placeholderMatches.length > 0;

  const handleSend = async () => {
    if (hasPlaceholders) return;
    await onSendSimulated(subject, body);
  };

  if (!email) {
    return (
      <div className="bg-white rounded-lg border border-slate-200 p-8 text-center text-slate-500 h-full flex flex-col items-center justify-center">
        <Sparkles className="w-8 h-8 text-blue-500 mb-2 animate-pulse" />
        <p className="text-sm font-medium text-slate-700">No Draft Email Generated Yet</p>
        <p className="text-xs text-slate-400 mt-1">Run single-pass analysis to auto-draft client chase email.</p>
      </div>
    );
  }

  const isSent = email.status === 'sent_simulated';

  return (
    <div className="bg-white rounded-lg border border-slate-200 shadow-sm flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-slate-200 bg-slate-50/50 flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-slate-900 text-sm flex items-center space-x-2">
            <span>AI Drafted Chase Email</span>
            {isSent ? (
              <span className="bg-emerald-100 text-emerald-800 text-[11px] font-semibold px-2 py-0.5 rounded-full border border-emerald-200 flex items-center space-x-1">
                <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                <span>Sent (Simulated Outbox)</span>
              </span>
            ) : (
              <span className="bg-blue-100 text-blue-800 text-[11px] font-semibold px-2 py-0.5 rounded-full border border-blue-200">
                Draft (Pending RM Approval)
              </span>
            )}
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Single consolidated email covering all gaps with plain English reasons.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          {!isSent && (
            <>
              <button
                onClick={() => setIsEditing(!isEditing)}
                className={`text-xs font-medium px-2.5 py-1 rounded border transition flex items-center space-x-1 ${isEditing ? 'bg-blue-50 text-blue-700 border-blue-300' : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-50'}`}
              >
                <FileEdit className="w-3.5 h-3.5" />
                <span>{isEditing ? 'Done Editing' : 'Edit Draft'}</span>
              </button>
              <button
                onClick={onReDraft}
                className="text-xs font-medium px-2 py-1 rounded bg-slate-100 text-slate-600 hover:bg-slate-200 transition"
                title="Re-run EmailDrafterAgent"
              >
                <Sparkles className="w-3.5 h-3.5 text-blue-600" />
              </button>
            </>
          )}
        </div>
      </div>

      {/* Editor Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Placeholder Warning Banner */}
        {hasPlaceholders && !isSent && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-900 flex items-start space-x-2">
            <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <strong className="font-semibold">Unresolved Placeholders Detected ({placeholderMatches.length})</strong>
              <p className="mt-0.5 text-amber-800">
                The draft contains placeholders like <code className="bg-amber-100 text-amber-900 px-1 py-0.5 rounded font-mono font-bold">[RM TO CONFIRM: deadline]</code>.
                Per Northgate Policy (Constraint C2), simulated send is disabled until you edit and replace all placeholders with verified values.
              </p>
            </div>
          </div>
        )}

        {/* Subject */}
        <div>
          <label className="block text-xs font-medium text-slate-700 mb-1">Subject</label>
          {isEditing ? (
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="w-full text-xs font-medium border border-slate-300 rounded p-2 focus:ring-1 focus:ring-blue-500 focus:outline-none"
            />
          ) : (
            <div className="text-xs font-semibold text-slate-900 bg-slate-50 border border-slate-200 rounded p-2">
              {subject}
            </div>
          )}
        </div>

        {/* Email Body */}
        <div>
          <label className="block text-xs font-medium text-slate-700 mb-1">Email Body</label>
          {isEditing ? (
            <textarea
              rows={12}
              value={body}
              onChange={(e) => setBody(e.target.value)}
              className="w-full text-xs font-mono border border-slate-300 rounded p-2.5 focus:ring-1 focus:ring-blue-500 focus:outline-none leading-relaxed"
            />
          ) : (
            <div className="text-xs text-slate-800 bg-slate-50 border border-slate-200 rounded p-3 leading-relaxed whitespace-pre-wrap font-sans">
              {body.split(/(\[RM TO CONFIRM:[^\]]+\])/g).map((part, idx) =>
                part.startsWith('[RM TO CONFIRM:') ? (
                  <span
                    key={idx}
                    className="bg-amber-200 text-amber-900 font-mono font-bold px-1.5 py-0.5 rounded border border-amber-300 inline-block shadow-sm animate-pulse"
                  >
                    {part}
                  </span>
                ) : (
                  part
                )
              )}
            </div>
          )}
        </div>

        {/* Guardrail Checklist */}
        {guardrailReport && (
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-3">
            <h4 className="text-xs font-semibold text-slate-800 flex items-center space-x-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-blue-600" />
              <span>Pre-Send Guardrail Audit</span>
            </h4>
            <div className="mt-2 space-y-1.5 text-[11px]">
              {guardrailReport.checks.map((check, i) => (
                <div key={i} className="flex items-start space-x-2">
                  {check.passed ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                  ) : (
                    <XCircle className="w-3.5 h-3.5 text-amber-600 shrink-0 mt-0.5" />
                  )}
                  <div>
                    <strong className="text-slate-700 capitalize font-medium">
                      {check.check_name.replace(/_/g, ' ')}:
                    </strong>{' '}
                    <span className="text-slate-600">{check.details}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* RM Operational Notes & Follow-ons */}
        {(email.notes_for_rm || possibleFollowons) && (
          <div className="bg-blue-50/70 border border-blue-200 rounded-lg p-3 space-y-2 text-xs">
            {email.notes_for_rm && (
              <div>
                <strong className="text-blue-900 flex items-center space-x-1">
                  <Info className="w-3.5 h-3.5 text-blue-600" />
                  <span>Notes for Relationship Manager:</span>
                </strong>
                <p className="text-blue-800 text-[11px] mt-0.5">{email.notes_for_rm}</p>
              </div>
            )}
            {possibleFollowons && (
              <div className="pt-2 border-t border-blue-200/60">
                <strong className="text-purple-900 flex items-center space-x-1">
                  <Lock className="w-3.5 h-3.5 text-purple-600" />
                  <span>Confidential Potential Follow-on (RM Only - NEVER Sent to Client):</span>
                </strong>
                <p className="text-purple-800 text-[11px] mt-0.5 font-medium">{possibleFollowons}</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer Send Action */}
      <div className="p-3 border-t border-slate-200 bg-slate-50/60 flex items-center justify-between">
        <div className="text-[11px] text-slate-500 flex items-center space-x-1">
          <Lock className="w-3 h-3 text-slate-400" />
          <span>Simulated Outbox (Constraint C2) - nothing leaves the system</span>
        </div>

        {!isSent && (
          <button
            onClick={handleSend}
            disabled={hasPlaceholders || isSending}
            title={hasPlaceholders ? 'Resolve all [RM TO CONFIRM: ...] placeholders to send' : 'Click to send simulated email'}
            className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-md font-semibold text-xs text-white bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed shadow-sm transition"
          >
            <Send className="w-3.5 h-3.5" />
            <span>{isSending ? 'Sending...' : 'Approve & Send (Simulated)'}</span>
          </button>
        )}
      </div>
    </div>
  );
};
