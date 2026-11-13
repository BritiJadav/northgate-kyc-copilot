import { apiFetch } from './client';
import {
  CompanySummary,
  AISuggestionItem,
  PossibleMatchItem,
  CompanyDocument,
  ConfirmedRecord,
  GraphNode,
  GraphEdge,
} from '../types/kyc';

export const kycApi = {
  listFiles: () => apiFetch<CompanySummary[]>('/api/kyc/files'),

  getFile: (id: number) =>
    apiFetch<{
      id: number;
      name: string;
      code: string;
      jurisdiction: string;
      registration_number: string;
      incorporation_date?: string | null;
      status: string;
      pending_decisions_count: number;
      documents: CompanyDocument[];
      all_decided: boolean;
    }>(`/api/kyc/files/${id}`),

  extractData: (id: number) =>
    apiFetch<{
      company_id: number;
      company_name: string;
      company_code: string;
      suggestions_count: number;
      unresolved_pct: number;
      has_cycles: boolean;
      graph_nodes: GraphNode[];
      graph_edges: GraphEdge[];
    }>(`/api/kyc/files/${id}/extract`, { method: 'POST' }),

  getSuggestions: (id: number) =>
    apiFetch<{
      company_id: number;
      company_name: string;
      code: string;
      status: string;
      suggestions: AISuggestionItem[];
      possible_matches: PossibleMatchItem[];
      all_decided: boolean;
    }>(`/api/kyc/files/${id}/suggestions`),

  recordDecision: (
    suggestionId: number,
    payload: {
      action: 'accept' | 'edit' | 'reject';
      final_value: string;
      reason_code?: string;
      rationale?: string;
      time_spent_ms?: number;
      source_opened?: boolean;
      analyst_id?: string;
    }
  ) =>
    apiFetch(`/api/kyc/suggestions/${suggestionId}/decision`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  addMissedParty: (
    companyId: number,
    payload: {
      party_name: string;
      role: string;
      ownership_pct?: number;
      voting_pct?: number;
      notes?: string;
      analyst_id?: string;
    }
  ) =>
    apiFetch(`/api/kyc/files/${companyId}/add-party`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  resolveMatch: (
    companyId: number,
    payload: {
      match_id: number;
      action: 'confirm_same' | 'confirm_different';
      analyst_id?: string;
    }
  ) =>
    apiFetch<{
      status: string;
      recomputed_lookthrough: any;
    }>(`/api/kyc/files/${companyId}/resolve-match`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  submitFile: (companyId: number, analystId: string = 'analyst_1') =>
    apiFetch<{
      status: string;
      message: string;
      confirmed_count: number;
    }>(`/api/kyc/files/${companyId}/submit`, {
      method: 'POST',
      body: JSON.stringify({ analyst_id: analystId }),
    }),

  getConfirmedRecords: (companyId: number) =>
    apiFetch<ConfirmedRecord[]>(`/api/kyc/files/${companyId}/confirmed`),
};
