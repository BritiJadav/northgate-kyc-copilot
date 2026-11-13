import { apiFetch } from './client';
import {
  ChaseCaseSummary,
  ChaseCaseDetail,
  GapRow,
  ChaseEmail,
  ReminderTask,
  GuardrailReport
} from '../types';

export const chaseApi = {
  listCases: () => apiFetch<ChaseCaseSummary[]>('/api/chase/cases'),

  getCase: (id: number) => apiFetch<ChaseCaseDetail>(`/api/chase/cases/${id}`),

  analyseCase: (id: number) =>
    apiFetch<{
      case_id: number;
      gaps: GapRow[];
      possible_followons?: string | null;
      draft_email: {
        id: number;
        subject: string;
        body: string;
        notes_for_rm?: string;
        guardrail_passed: boolean;
        guardrail_report: GuardrailReport;
      };
    }>(`/api/chase/cases/${id}/analyse`, { method: 'POST' }),

  reDraftEmail: (id: number) =>
    apiFetch<{
      email: ChaseEmail;
      guardrail: GuardrailReport;
    }>(`/api/chase/cases/${id}/draft`, { method: 'POST' }),

  updateGap: (gapId: number, payload: { is_active?: boolean; notes?: string; reason?: string }) =>
    apiFetch<GapRow>(`/api/chase/gaps/${gapId}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),

  addGap: (caseId: number, payload: { party_name: string; requirement: string; notes?: string }) =>
    apiFetch<GapRow>(`/api/chase/cases/${caseId}/gaps`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  sendEmailSimulated: (
    emailId: number,
    payload: { subject?: string; body?: string; actor_id: string }
  ) =>
    apiFetch<{
      status: string;
      message: string;
      email_id: number;
      case_id: number;
      sent_at: string;
    }>(`/api/chase/emails/${emailId}/send`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  simulateReply: (
    caseId: number,
    payload: { documents: Array<{ filename: string; doc_type?: string; signed?: boolean; pages_present?: string }> }
  ) =>
    apiFetch<{
      case_id: number;
      rounds_count: number;
      last_contact_date: string;
      analysis: any;
    }>(`/api/chase/cases/${caseId}/simulate-reply`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  listTasks: () => apiFetch<ReminderTask[]>('/api/chase/tasks'),

  snoozeTask: (taskId: number, payload: { snooze_days: number; reason: string }) =>
    apiFetch<ReminderTask>(`/api/chase/tasks/${taskId}/snooze`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  completeTask: (taskId: number) =>
    apiFetch<{ status: string; task_id: number }>(`/api/chase/tasks/${taskId}/complete`, {
      method: 'POST',
    }),
};
