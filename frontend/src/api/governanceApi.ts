import { apiFetch } from './client';

export interface ControlCheckItem {
  id: string;
  name: string;
  description: string;
  status: 'PASS' | 'FAIL';
  details: string;
}

export interface GovernanceChecklistResponse {
  status: string;
  pilot_mode: string;
  demo_mode: boolean;
  total_controls: number;
  passed_controls: number;
  checks: ControlCheckItem[];
}

export interface PilotModeResponse {
  pilot_mode: string;
  demo_mode: boolean;
  canary_share: number;
  description: string;
}

export interface ConfirmedRecordItem {
  id: number;
  company_id: number;
  company_code: string;
  company_name: string;
  field_name: string;
  value: string;
  field_type: string;
  formula?: string | null;
  source_citation?: string | null;
  confirmed_by: string;
  as_at?: string | null;
  created_at?: string | null;
}

export interface EvalReportResponse {
  timestamp: string;
  duration_seconds: number;
  overall_status: 'PASS' | 'FAIL';
  summary: {
    module_a_gap_f1: number;
    module_a_guardrail_accuracy: number;
    module_b_companies_passed: number;
    module_b_companies_total: number;
    kestrel_failure_modes_passed: number;
    citation_verifier_accuracy: number;
  };
  module_a: any;
  module_b: any;
}

export const governanceApi = {
  getChecklist: () => apiFetch<GovernanceChecklistResponse>('/api/governance/checklist'),
  getMode: () => apiFetch<PilotModeResponse>('/api/governance/mode'),
  updateMode: (mode: 'assisted' | 'shadow') =>
    apiFetch<{ status: string; new_mode: string; message: string }>('/api/governance/mode', {
      method: 'POST',
      body: JSON.stringify({ mode }),
    }),
  getConfirmedRecords: () => apiFetch<ConfirmedRecordItem[]>('/api/governance/confirmed-records'),
  getEvalReport: () => apiFetch<EvalReportResponse>('/api/governance/eval'),
  runEval: () => apiFetch<EvalReportResponse>('/api/governance/eval/run', { method: 'POST' }),
};
