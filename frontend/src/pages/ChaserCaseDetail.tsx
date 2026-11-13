import React, { useState } from 'react';
import { useParams, NavLink } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { chaseApi } from '../api/chaseApi';
import { GapTable } from '../components/GapTable';
import { EmailEditor } from '../components/EmailEditor';
import { Timeline } from '../components/Timeline';
import {
  FileSearch,
  ArrowLeft,
  Sparkles,
  Users,
  FileText,
  Clock,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  MessageSquareShare
} from 'lucide-react';

export const ChaserCaseDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const caseId = parseInt(id || '1', 10);
  const queryClient = useQueryClient();

  const [showReplyModal, setShowReplyModal] = useState(false);
  const [replyDocName, setReplyDocName] = useState('updated_passport.pdf');
  const [replyDocType, setReplyDocType] = useState('Passport');

  // Fetch full case detail
  const { data: caseDetail, isLoading, error } = useQuery({
    queryKey: ['chaseCase', caseId],
    queryFn: () => chaseApi.getCase(caseId),
  });

  // Run full analysis mutation
  const analyseMutation = useMutation({
    mutationFn: () => chaseApi.analyseCase(caseId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chaseCase', caseId] });
      queryClient.invalidateQueries({ queryKey: ['agentRuns'] });
    },
  });

  // Re-draft email mutation
  const reDraftMutation = useMutation({
    mutationFn: () => chaseApi.reDraftEmail(caseId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chaseCase', caseId] });
    },
  });

  // Toggle gap active mutation
  const toggleGapMutation = useMutation({
    mutationFn: ({ gapId, isActive, reason }: { gapId: number; isActive: boolean; reason?: string }) =>
      chaseApi.updateGap(gapId, { is_active: isActive, reason }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chaseCase', caseId] });
    },
  });

  // Add custom gap mutation
  const addGapMutation = useMutation({
    mutationFn: (payload: { party_name: string; requirement: string; notes?: string }) =>
      chaseApi.addGap(caseId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chaseCase', caseId] });
    },
  });

  // Send simulated email mutation
  const sendMutation = useMutation({
    mutationFn: ({ emailId, subject, body }: { emailId: number; subject: string; body: string }) =>
      chaseApi.sendEmailSimulated(emailId, { subject, body, actor_id: 'RM_Current' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chaseCase', caseId] });
      queryClient.invalidateQueries({ queryKey: ['chaseCases'] });
    },
  });

  // Simulate client reply mutation
  const replyMutation = useMutation({
    mutationFn: (docs: Array<{ filename: string; doc_type?: string; signed?: boolean }>) =>
      chaseApi.simulateReply(caseId, { documents: docs }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chaseCase', caseId] });
      setShowReplyModal(false);
    },
  });

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12 text-center text-slate-500">
        Loading case workspace...
      </div>
    );
  }

  if (error || !caseDetail) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8 text-rose-600">
        Case not found or failed to load.
      </div>
    );
  }

  const latestDraft = caseDetail.emails?.[caseDetail.emails.length - 1] || null;

  return (
    <div className="max-w-[1700px] mx-auto px-4 py-6 space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <div className="flex items-center space-x-4">
          <NavLink
            to="/chaser"
            className="p-1.5 rounded-md hover:bg-slate-100 text-slate-500 hover:text-slate-800 transition"
          >
            <ArrowLeft className="w-5 h-5" />
          </NavLink>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-mono text-xs font-semibold text-slate-500">{caseDetail.case_number}</span>
              <span className="text-slate-300">|</span>
              <span className="bg-slate-100 px-2 py-0.5 rounded text-[11px] font-medium text-slate-700 capitalize">
                {caseDetail.client_type}
              </span>
              <span className="bg-blue-100 text-blue-800 text-[11px] font-semibold px-2 py-0.5 rounded">
                Round {caseDetail.rounds_count}
              </span>
            </div>
            <h1 className="text-xl font-bold text-slate-900 mt-0.5">{caseDetail.client_name}</h1>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-2.5">
          <button
            onClick={() => analyseMutation.mutate()}
            disabled={analyseMutation.isPending}
            className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-lg text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 shadow-sm transition"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{analyseMutation.isPending ? 'Analysing...' : 'Run Single-Pass Analysis'}</span>
          </button>

          <button
            onClick={() => setShowReplyModal(true)}
            className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-lg text-xs font-medium text-slate-700 bg-white border border-slate-300 hover:bg-slate-50 shadow-sm transition"
            title="Simulate client providing documents (tests partial-reply cadence reset)"
          >
            <MessageSquareShare className="w-3.5 h-3.5 text-blue-600" />
            <span>Simulate Client Reply</span>
          </button>
        </div>
      </div>

      {/* Main 3-Column RM Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 min-h-[640px]">
        {/* Left Column: Parties & Received Documents (3 cols) */}
        <div className="lg:col-span-3 space-y-5">
          {/* Parties List */}
          <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-4">
            <h3 className="font-semibold text-xs text-slate-900 flex items-center space-x-1.5 uppercase tracking-wider mb-3">
              <Users className="w-3.5 h-3.5 text-blue-600" />
              <span>Identified Parties ({caseDetail.parties.length})</span>
            </h3>

            <div className="space-y-2">
              {caseDetail.parties.map((p) => (
                <div key={p.id} className="bg-slate-50 border border-slate-200/80 rounded p-2.5 text-xs">
                  <div className="font-semibold text-slate-900">{p.name}</div>
                  <div className="text-[11px] text-slate-600 flex items-center justify-between mt-1">
                    <span className="capitalize">{p.role.replace(/_/g, ' ')}</span>
                    {p.ownership_pct !== null && p.ownership_pct !== undefined && (
                      <span className="font-mono font-medium text-blue-700 bg-blue-50 px-1.5 py-0.2 rounded">
                        {p.ownership_pct}%
                      </span>
                    )}
                  </div>
                  {p.dob && (
                    <div className="text-[10px] text-slate-400 mt-1">
                      DOB: {p.dob} {p.nationality && `(${p.nationality})`}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Received Documents with Observable Facts */}
          <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-4">
            <h3 className="font-semibold text-xs text-slate-900 flex items-center space-x-1.5 uppercase tracking-wider mb-3">
              <FileText className="w-3.5 h-3.5 text-blue-600" />
              <span>Received Documents ({caseDetail.documents.length})</span>
            </h3>

            <div className="space-y-2">
              {caseDetail.documents.length === 0 ? (
                <p className="text-xs text-slate-400">No documents received yet.</p>
              ) : (
                caseDetail.documents.map((doc) => (
                  <div key={doc.id} className="bg-slate-50 border border-slate-200/80 rounded p-2.5 text-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-800 truncate" title={doc.filename}>
                        {doc.filename}
                      </span>
                      <a
                        href={`/documents/${doc.filename}`}
                        target="_blank"
                        rel="noreferrer"
                        className="text-blue-600 hover:text-blue-800"
                        title="View Document"
                      >
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>

                    <div className="text-[11px] text-slate-600">
                      <strong>Type:</strong> {doc.doc_type || 'Unclassified'}
                    </div>

                    {doc.pages_present && (
                      <div className="text-[11px] text-slate-600">
                        <strong>Pages:</strong> {doc.pages_present}
                      </div>
                    )}

                    {doc.expiry_date && (
                      <div className="text-[11px] text-slate-600">
                        <strong>Expiry:</strong> {doc.expiry_date}
                      </div>
                    )}

                    {doc.issue_date && (
                      <div className="text-[11px] text-slate-600">
                        <strong>Issue Date:</strong> {doc.issue_date}
                      </div>
                    )}

                    <div className="text-[10px] text-slate-400 flex items-center justify-between pt-1">
                      <span>Signed: {doc.signed === true ? 'Yes' : doc.signed === false ? 'No' : 'Unknown'}</span>
                      <span className="text-emerald-700 bg-emerald-50 px-1 rounded">Facts only (C3)</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Center Column: Deterministic Gap Matrix (5 cols) */}
        <div className="lg:col-span-5 h-full">
          <GapTable
            gaps={caseDetail.gaps}
            parties={caseDetail.parties}
            onToggleGap={async (gapId, isActive, reason) => {
              await toggleGapMutation.mutateAsync({ gapId, isActive, reason });
            }}
            onAddGap={async (payload) => {
              await addGapMutation.mutateAsync(payload);
            }}
          />
        </div>

        {/* Right Column: AI Draft Email & Guardrails (4 cols) */}
        <div className="lg:col-span-4 h-full">
          <EmailEditor
            email={latestDraft}
            possibleFollowons={caseDetail.possible_followons}
            isSending={sendMutation.isPending}
            onSendSimulated={async (subject, body) => {
              if (latestDraft) {
                await sendMutation.mutateAsync({ emailId: latestDraft.id, subject, body });
              }
            }}
            onReDraft={async () => {
              await reDraftMutation.mutateAsync();
            }}
          />
        </div>
      </div>

      {/* Bottom Timeline */}
      <Timeline
        emails={caseDetail.emails}
        reminders={caseDetail.reminders}
        documents={caseDetail.documents}
        lastContactDate={caseDetail.last_contact_date}
      />

      {/* Simulate Client Reply Modal */}
      {showReplyModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl border border-slate-200 max-w-md w-full p-5">
            <h4 className="font-semibold text-slate-900 text-sm">Simulate Client Submission (Reply)</h4>
            <p className="text-xs text-slate-500 mt-1">
              Simulates a client submitting documents. Demonstrates how the system re-evaluates remaining gaps,
              restarts the 3-day clock for remaining items, and increments rounds.
            </p>

            <div className="mt-4 space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-700">Document Filename</label>
                <input
                  type="text"
                  value={replyDocName}
                  onChange={(e) => setReplyDocName(e.target.value)}
                  className="mt-1 block w-full text-xs rounded border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700">Document Type</label>
                <input
                  type="text"
                  value={replyDocType}
                  onChange={(e) => setReplyDocType(e.target.value)}
                  className="mt-1 block w-full text-xs rounded border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"
                />
              </div>
            </div>

            <div className="mt-5 flex justify-end space-x-2 pt-2 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setShowReplyModal(false)}
                className="px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-100 rounded"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => {
                  replyMutation.mutate([
                    {
                      filename: replyDocName,
                      doc_type: replyDocType,
                      signed: true,
                    },
                  ]);
                }}
                disabled={replyMutation.isPending}
                className="px-3.5 py-1.5 text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white rounded shadow-sm disabled:opacity-50"
              >
                {replyMutation.isPending ? 'Simulating...' : 'Submit Client Reply'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
