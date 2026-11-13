import { apiFetch } from './client';
import { AgentRun, AuditLogEntry } from '../types';

export const adminApi = {
  getClock: () => apiFetch<{ simulated_date: string }>('/api/admin/clock'),

  advanceClock: (days: number = 1) =>
    apiFetch<{
      old_date: string;
      new_date: string;
      advanced_business_days: number;
      new_tasks_triggered_count: number;
      triggered_tasks: Array<{ id: number; title: string; day_number: number }>;
    }>(`/api/admin/advance-clock?days=${days}`, { method: 'POST' }),

  resetDemo: () =>
    apiFetch<{ status: string; message: string }>('/api/admin/reset-demo', {
      method: 'POST',
    }),

  getAuditTrail: (caseId?: number, companyId?: number) => {
    let url = '/api/admin/audit?limit=50';
    if (caseId) url += `&case_id=${caseId}`;
    if (companyId) url += `&company_id=${companyId}`;
    return apiFetch<AuditLogEntry[]>(url);
  },

  getAgentRuns: () => apiFetch<AgentRun[]>('/api/admin/agent-runs?limit=30'),

  getHealth: () =>
    apiFetch<{
      status: string;
      demo_mode: boolean;
      simulated_date: string;
      pilot_mode: string;
      synthetic_notice: string;
    }>('/health'),
};
