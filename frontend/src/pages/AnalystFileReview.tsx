import React, { useState, useEffect, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import { kycApi } from '../api/kycApi';
import {
  AISuggestionItem,
  PossibleMatchItem,
  CompanyDocument,
  GraphNode,
  GraphEdge,
} from '../types/kyc';
import { ConfirmRow } from '../components/ConfirmRow';
import { PdfViewer } from '../components/PdfViewer';
import { PossibleMatchCard } from '../components/PossibleMatchCard';
import { OwnershipGraph } from '../components/OwnershipGraph';

export const AnalystFileReview: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const companyId = parseInt(id || '1', 10);

  const [company, setCompany] = useState<any>(null);
  const [documents, setDocuments] = useState<CompanyDocument[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<CompanyDocument | null>(null);
  const [suggestions, setSuggestions] = useState<AISuggestionItem[]>([]);
  const [possibleMatches, setPossibleMatches] = useState<PossibleMatchItem[]>([]);
  const [allDecided, setAllDecided] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [isExtracting, setIsExtracting] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Active citation highlight
  const [activeCitation, setActiveCitation] = useState<{
    docName: string;
    page: number;
    line: number;
    quote?: string;
  } | null>(null);

  // Graph toggle
  const [showGraph, setShowGraph] = useState<boolean>(false);
  const [graphData, setGraphData] = useState<{ nodes: GraphNode[]; edges: GraphEdge[] }>({
    nodes: [],
    edges: [],
  });

  // Add party modal
  const [showAddPartyModal, setShowAddPartyModal] = useState<boolean>(false);
  const [newPartyName, setNewPartyName] = useState('');
  const [newPartyRole, setNewPartyRole] = useState('Shareholder');
  const [newPartyOwnership, setNewPartyOwnership] = useState<string>('');
  const [newPartyVoting, setNewPartyVoting] = useState<string>('');
  const [newPartyNotes, setNewPartyNotes] = useState('');
  const [isAddingParty, setIsAddingParty] = useState(false);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const fileData = await kycApi.getFile(companyId);
      setCompany(fileData);
      setDocuments(fileData.documents || []);
      if (fileData.documents && fileData.documents.length > 0 && !selectedDoc) {
        setSelectedDoc(fileData.documents[0]);
      }

      const suggData = await kycApi.getSuggestions(companyId);
      setSuggestions(suggData.suggestions || []);
      setPossibleMatches(suggData.possible_matches || []);
      setAllDecided(suggData.all_decided);
    } catch (err: any) {
      setError(err?.message || 'Failed to load company review data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (companyId) {
      loadData();
    }
  }, [companyId]);

  const handleExtract = async () => {
    setIsExtracting(true);
    setError(null);
    try {
      const res = await kycApi.extractData(companyId);
      if (res.graph_nodes && res.graph_edges) {
        setGraphData({ nodes: res.graph_nodes, edges: res.graph_edges });
      }
      await loadData();
    } catch (err: any) {
      setError(err?.message || 'Extraction failed');
    } finally {
      setIsExtracting(false);
    }
  };

  const handleSelectCitation = (doc: string, page: number, line: number, quote?: string) => {
    setActiveCitation({ docName: doc, page, line, quote });
    // Match document
    const foundDoc = documents.find(
      (d) => d.filename.toLowerCase() === doc.toLowerCase() || d.filename.includes(doc) || doc.includes(d.filename)
    );
    if (foundDoc) {
      setSelectedDoc(foundDoc);
    }
  };

  const handleDecision = async (
    suggestionId: number,
    payload: {
      action: 'accept' | 'edit' | 'reject';
      final_value: string;
      reason_code?: string;
      rationale?: string;
      time_spent_ms?: number;
      source_opened?: boolean;
    }
  ) => {
    try {
      await kycApi.recordDecision(suggestionId, payload);
      // Refresh suggestions
      const suggData = await kycApi.getSuggestions(companyId);
      setSuggestions(suggData.suggestions || []);
      setAllDecided(suggData.all_decided);
    } catch (err: any) {
      alert(`Decision recording failed: ${err?.message || err}`);
    }
  };

  const handleResolveMatch = async (matchId: number, action: 'confirm_same' | 'confirm_different') => {
    try {
      await kycApi.resolveMatch(companyId, { match_id: matchId, action });
      await loadData();
    } catch (err: any) {
      alert(`Candidate match resolution failed: ${err?.message || err}`);
    }
  };

  const handleAddParty = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPartyName.trim()) return;
    setIsAddingParty(true);
    try {
      await kycApi.addMissedParty(companyId, {
        party_name: newPartyName.trim(),
        role: newPartyRole,
        ownership_pct: newPartyOwnership ? parseFloat(newPartyOwnership) : undefined,
        voting_pct: newPartyVoting ? parseFloat(newPartyVoting) : undefined,
        notes: newPartyNotes.trim() || undefined,
      });
      setShowAddPartyModal(false);
      setNewPartyName('');
      setNewPartyOwnership('');
      setNewPartyVoting('');
      setNewPartyNotes('');
      await loadData();
    } catch (err: any) {
      alert(`Failed to add missed party: ${err?.message || err}`);
    } finally {
      setIsAddingParty(false);
    }
  };

  const handleSubmitFile = async () => {
    if (!allDecided) {
      alert('Cannot submit file: all suggestions must be accepted, edited, or rejected by human analyst.');
      return;
    }
    const pendingMatches = possibleMatches.filter((m) => m.status === 'pending');
    if (pendingMatches.length > 0) {
      alert('Cannot submit file: all candidate matches must be confirmed or separated.');
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await kycApi.submitFile(companyId);
      setSubmitSuccess(res.message || `File successfully confirmed! (${res.confirmed_count} records saved)`);
      await loadData();
    } catch (err: any) {
      alert(`Submission failed: ${err?.message || err}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Group suggestions
  const groupedSuggestions = useMemo(() => {
    const groups: {
      ubos: AISuggestionItem[];
      voting: AISuggestionItem[];
      control: AISuggestionItem[];
      holdings: AISuggestionItem[];
      other: AISuggestionItem[];
    } = {
      ubos: [],
      voting: [],
      control: [],
      holdings: [],
      other: [],
    };

    suggestions.forEach((s) => {
      const name = s.field_name.toLowerCase();
      if (name.includes('ubo') || name.includes('look-through') || name.includes('ultimate beneficial')) {
        groups.ubos.push(s);
      } else if (name.includes('voting') || name.includes('vote')) {
        groups.voting.push(s);
      } else if (name.includes('nominee') || name.includes('control') || name.includes('board') || name.includes('trustee') || name.includes('poa')) {
        groups.control.push(s);
      } else if (name.includes('direct holding') || name.includes('holds') || name.includes('shares')) {
        groups.holdings.push(s);
      } else {
        groups.other.push(s);
      }
    });

    return groups;
  }, [suggestions]);

  const decidedCount = suggestions.filter((s) => s.has_decision).length;
  const totalCount = suggestions.length;
  const pendingMatchCount = possibleMatches.filter((m) => m.status === 'pending').length;
  const canSubmit = totalCount > 0 && decidedCount === totalCount && pendingMatchCount === 0;

  if (loading && !company) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mb-3" />
        <p className="text-sm text-slate-600">Loading KYC file review workspace...</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-5">
      {/* Top Breadcrumb & Metadata */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2 text-xs text-slate-500 mb-1">
            <Link to="/analyst" className="hover:text-indigo-600 hover:underline">
              Analyst Assist Files
            </Link>
            <span>/</span>
            <span className="font-semibold text-slate-700">{company?.code}</span>
          </div>
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold text-slate-900">{company?.name}</h1>
            <span className="font-mono text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-300">
              {company?.jurisdiction} • Reg #{company?.registration_number}
            </span>
            {company?.status === 'submitted' && (
              <span className="bg-emerald-100 text-emerald-800 text-xs px-2.5 py-0.5 rounded-full font-semibold border border-emerald-300">
                Confirmed & Submitted
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <button
            type="button"
            onClick={handleExtract}
            disabled={isExtracting}
            className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border border-indigo-300 shadow-sm transition-colors"
          >
            <svg
              className={`w-3.5 h-3.5 mr-1.5 ${isExtracting ? 'animate-spin' : ''}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            {isExtracting ? 'Extracting with Gemini...' : 'Re-run AI Extraction'}
          </button>

          <button
            type="button"
            onClick={() => setShowAddPartyModal(true)}
            className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold bg-white text-slate-700 hover:bg-slate-50 border border-slate-300 shadow-sm transition-colors"
          >
            <svg className="w-3.5 h-3.5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add Missed Party
          </button>

          <button
            type="button"
            onClick={() => setShowGraph(!showGraph)}
            className={`inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold border shadow-sm transition-colors ${
              showGraph
                ? 'bg-purple-600 text-white border-purple-700'
                : 'bg-white text-purple-700 hover:bg-purple-50 border-purple-300'
            }`}
          >
            <svg className="w-3.5 h-3.5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
            </svg>
            {showGraph ? 'Hide Ownership Graph' : 'View Ownership Graph'}
          </button>
        </div>
      </div>

      {/* Submission Success Alert */}
      {submitSuccess && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-900 p-4 rounded-lg text-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <span className="font-medium">{submitSuccess}</span>
          </div>
          <Link
            to="/governance"
            className="text-xs font-semibold text-emerald-700 hover:text-emerald-900 underline"
          >
            View in Confirmed Records Governance
          </Link>
        </div>
      )}

      {/* Progress & Verification Bar */}
      <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-700 uppercase tracking-wide">
              Review Progress:
            </span>
            <span className="text-xs font-bold text-slate-900">
              {decidedCount} of {totalCount} fields verified ({totalCount > 0 ? Math.round((decidedCount / totalCount) * 100) : 0}%)
            </span>
          </div>
          <div className="w-64 bg-slate-100 rounded-full h-2 overflow-hidden border border-slate-200">
            <div
              className={`h-full transition-all duration-300 ${
                decidedCount === totalCount && totalCount > 0 ? 'bg-emerald-500' : 'bg-indigo-600'
              }`}
              style={{ width: `${totalCount > 0 ? (decidedCount / totalCount) * 100 : 0}%` }}
            />
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-500">
            Constraint C9: Human must accept/edit/reject each field individually.
          </span>
          <button
            type="button"
            disabled={!canSubmit || isSubmitting}
            onClick={handleSubmitFile}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all shadow-sm ${
              canSubmit
                ? 'bg-emerald-600 hover:bg-emerald-700 text-white cursor-pointer'
                : 'bg-slate-100 text-slate-400 border border-slate-200 cursor-not-allowed'
            }`}
            title={
              !canSubmit
                ? pendingMatchCount > 0
                  ? 'Resolve all candidate matches first'
                  : 'Verify all suggestions before submitting'
                : 'Submit confirmed records to downstream KYC ledger'
            }
          >
            {isSubmitting ? 'Submitting...' : 'Submit Confirmed KYC File'}
          </button>
        </div>
      </div>

      {/* Candidate Matches Section (C8) */}
      {possibleMatches.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-amber-900 uppercase tracking-wide flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-amber-500" />
              C8 Entity Resolution Candidates ({possibleMatches.length})
            </h3>
            <span className="text-xs text-amber-700 italic">
              "Never auto-merged: confirm or separate before final submission"
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {possibleMatches.map((m) => (
              <PossibleMatchCard key={m.id} match={m} onResolve={handleResolveMatch} />
            ))}
          </div>
        </div>
      )}

      {/* Embedded Ownership Graph */}
      {showGraph && (
        <div className="bg-white rounded-xl border border-purple-200 p-4 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-purple-900">
              Interactive Look-Through Ownership Graph (NetworkX Multi-Tier)
            </h3>
            <button
              onClick={() => setShowGraph(false)}
              className="text-xs text-slate-500 hover:text-slate-800"
            >
              Close Graph
            </button>
          </div>
          <OwnershipGraph
            companyName={company?.name || 'Company'}
            nodes={graphData.nodes}
            edges={graphData.edges}
          />
        </div>
      )}

      {/* Split Review Workspace: Left = PDF Viewer, Right = Suggestions List */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Left: Document Viewer (5 cols) */}
        <div className="lg:col-span-5 space-y-3">
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden sticky top-4">
            <PdfViewer
              documents={documents}
              activeDoc={selectedDoc?.filename || (documents[0]?.filename ?? '')}
              onSelectDoc={(filename) => {
                const found = documents.find((d) => d.filename === filename);
                if (found) setSelectedDoc(found);
              }}
              highlightLine={
                activeCitation
                  ? {
                      doc: activeCitation.docName,
                      page: activeCitation.page,
                      line: activeCitation.line,
                      quote: activeCitation.quote,
                    }
                  : null
              }
            />
          </div>
        </div>

        {/* Right: AI Suggestions & Human Decisions (7 cols) */}
        <div className="lg:col-span-7 space-y-5">
          {suggestions.length === 0 ? (
            <div className="bg-white rounded-xl border border-slate-200 p-8 text-center shadow-sm space-y-3">
              <svg className="w-12 h-12 text-slate-300 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 className="text-sm font-bold text-slate-800">No Extracted Data Yet</h3>
              <p className="text-xs text-slate-500 max-w-md mx-auto">
                Click "Run AI Extraction" to parse incorporation documents, compute look-through ownership, and extract verifiable line citations.
              </p>
              <button
                type="button"
                onClick={handleExtract}
                disabled={isExtracting}
                className="inline-flex items-center px-4 py-2 rounded-lg text-xs font-semibold bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm"
              >
                {isExtracting ? 'Extracting with Gemini...' : 'Extract Data Now'}
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Group 1: Look-Through UBOs */}
              {groupedSuggestions.ubos.length > 0 && (
                <div className="space-y-2.5">
                  <div className="flex items-center justify-between border-b border-purple-200 pb-1.5">
                    <h3 className="text-xs font-bold text-purple-900 uppercase tracking-wider flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-purple-600" />
                      Look-Through Beneficial Ownership (&gt;=25% Threshold)
                    </h3>
                    <span className="text-[11px] text-purple-700 font-mono">
                      C6: Deterministic Math
                    </span>
                  </div>
                  <div className="space-y-2">
                    {groupedSuggestions.ubos.map((s) => (
                      <ConfirmRow
                        key={s.id}
                        suggestion={s}
                        onSelectCitation={handleSelectCitation}
                        onDecision={handleDecision}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Group 2: Voting Rights */}
              {groupedSuggestions.voting.length > 0 && (
                <div className="space-y-2.5">
                  <div className="flex items-center justify-between border-b border-indigo-200 pb-1.5">
                    <h3 className="text-xs font-bold text-indigo-900 uppercase tracking-wider flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-indigo-600" />
                      Voting Rights & Share Classes
                    </h3>
                    <span className="text-[11px] text-indigo-700 font-mono">
                      Calculated from Articles of Association
                    </span>
                  </div>
                  <div className="space-y-2">
                    {groupedSuggestions.voting.map((s) => (
                      <ConfirmRow
                        key={s.id}
                        suggestion={s}
                        onSelectCitation={handleSelectCitation}
                        onDecision={handleDecision}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Group 3: Control & Nominee Flags */}
              {groupedSuggestions.control.length > 0 && (
                <div className="space-y-2.5">
                  <div className="flex items-center justify-between border-b border-slate-200 pb-1.5">
                    <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-slate-600" />
                      Control, Nominee & Governance Flags
                    </h3>
                  </div>
                  <div className="space-y-2">
                    {groupedSuggestions.control.map((s) => (
                      <ConfirmRow
                        key={s.id}
                        suggestion={s}
                        onSelectCitation={handleSelectCitation}
                        onDecision={handleDecision}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Group 4: Direct Holdings & Intermediate Edges */}
              {groupedSuggestions.holdings.length > 0 && (
                <div className="space-y-2.5">
                  <div className="flex items-center justify-between border-b border-blue-200 pb-1.5">
                    <h3 className="text-xs font-bold text-blue-900 uppercase tracking-wider flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-blue-600" />
                      Direct Shareholdings (Ownership Graph Edges)
                    </h3>
                  </div>
                  <div className="space-y-2">
                    {groupedSuggestions.holdings.map((s) => (
                      <ConfirmRow
                        key={s.id}
                        suggestion={s}
                        onSelectCitation={handleSelectCitation}
                        onDecision={handleDecision}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Group 5: Other Extracted Fields */}
              {groupedSuggestions.other.length > 0 && (
                <div className="space-y-2.5">
                  <div className="flex items-center justify-between border-b border-slate-200 pb-1.5">
                    <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-slate-400" />
                      Other Document Observations
                    </h3>
                  </div>
                  <div className="space-y-2">
                    {groupedSuggestions.other.map((s) => (
                      <ConfirmRow
                        key={s.id}
                        suggestion={s}
                        onSelectCitation={handleSelectCitation}
                        onDecision={handleDecision}
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Add Missed Party Modal */}
      {showAddPartyModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <h3 className="text-sm font-bold text-slate-900">
                Add a Party the AI Missed
              </h3>
              <button
                type="button"
                onClick={() => setShowAddPartyModal(false)}
                className="text-slate-400 hover:text-slate-600 text-lg"
              >
                &times;
              </button>
            </div>

            <form onSubmit={handleAddParty} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Party Name <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={newPartyName}
                  onChange={(e) => setNewPartyName(e.target.value)}
                  placeholder="e.g. John Doe / Apex Trust"
                  className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Role <span className="text-rose-500">*</span>
                </label>
                <select
                  value={newPartyRole}
                  onChange={(e) => setNewPartyRole(e.target.value)}
                  className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="Shareholder">Shareholder</option>
                  <option value="Director">Director</option>
                  <option value="Trustee">Trustee</option>
                  <option value="Nominee">Nominee Shareholder</option>
                  <option value="Beneficiary">Beneficiary</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Ownership %
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="100"
                    value={newPartyOwnership}
                    onChange={(e) => setNewPartyOwnership(e.target.value)}
                    placeholder="e.g. 25.0"
                    className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Voting %
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="100"
                    value={newPartyVoting}
                    onChange={(e) => setNewPartyVoting(e.target.value)}
                    placeholder="e.g. 25.0"
                    className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Notes / Source Reference
                </label>
                <textarea
                  rows={2}
                  value={newPartyNotes}
                  onChange={(e) => setNewPartyNotes(e.target.value)}
                  placeholder="e.g. Found on page 3 of the supplemental share registry..."
                  className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-200">
                <button
                  type="button"
                  onClick={() => setShowAddPartyModal(false)}
                  className="px-3 py-1.5 rounded-lg text-xs border border-slate-300 text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isAddingParty || !newPartyName.trim()}
                  className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 hover:bg-indigo-700 text-white disabled:opacity-50"
                >
                  {isAddingParty ? 'Adding...' : 'Add Party'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
