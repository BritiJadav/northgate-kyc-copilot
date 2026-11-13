export type GapStatus =
  | 'OK'
  | 'MISSING'
  | 'EXPIRED'
  | 'STALE'
  | 'INCOMPLETE'
  | 'WRONG_TYPE'
  | 'UNSIGNED'
  | 'NAME_MISMATCH';

export interface Party {
  id: number;
  case_id: number;
  name: string;
  role: string;
  ownership_pct?: number | null;
  dob?: string | null;
  nationality?: string | null;
}

export interface ReceivedDocument {
  id: number;
  case_id: number;
  party_id?: number | null;
  filename: string;
  file_path: string;
  doc_type?: string | null;
  party_name?: string | null;
  issue_date?: string | null;
  expiry_date?: string | null;
  page_count: number;
  pages_present?: string | null;
  signed?: boolean | null;
  created_at: string;
}

export interface GapRow {
  id: number;
  case_id: number;
  party_name: string;
  party_role?: string;
  requirement: string;
  status: GapStatus;
  evidence?: string | null;
  rule_id: string;
  is_active: boolean;
  notes?: string | null;
}

export interface GuardrailCheckItem {
  check_name: string;
  passed: boolean;
  details: string;
}

export interface GuardrailReport {
  passed: boolean;
  checks: GuardrailCheckItem[];
  reasons: string[];
  has_unresolved_placeholders: boolean;
}

export interface ChaseEmail {
  id: number;
  case_id: number;
  subject: string;
  body: string;
  notes_for_rm?: string | null;
  possible_followons?: string | null;
  status: 'draft' | 'approved' | 'sent_simulated';
  guardrail_passed: boolean;
  guardrail_report?: string | null;
  edits_diff?: string | null;
  sent_at?: string | null;
  created_at: string;
}

export interface ReminderTask {
  id: number;
  case_id: number;
  day_number: number;
  task_type: 'email_reminder' | 'phone_call' | 'manager_flag';
  title: string;
  pre_drafted_text?: string | null;
  status: 'pending' | 'completed' | 'snoozed';
  snoozed_until?: string | null;
  snooze_reason?: string | null;
  triggered_at: string;
  case_client_name?: string | null;
}

export interface ChaseCaseSummary {
  id: number;
  case_number: string;
  client_name: string;
  client_type: string;
  status: string;
  rm_name: string;
  deadline?: string | null;
  last_contact_date?: string | null;
  rounds_count: number;
  gap_count: number;
  created_at: string;
}

export interface ChaseCaseDetail extends ChaseCaseSummary {
  parties: Party[];
  documents: ReceivedDocument[];
  gaps: GapRow[];
  emails: ChaseEmail[];
  reminders: ReminderTask[];
  possible_followons?: string | null;
}

export interface AgentRun {
  id: number;
  agent_name: string;
  prompt_version: string;
  input_hash: string;
  latency_ms: number;
  tokens_used: number;
  cache_hit: boolean;
  status: string;
  created_at: string;
}

export interface AuditLogEntry {
  id: number;
  case_id?: number | null;
  company_id?: number | null;
  entity_type: string;
  entity_id?: number | null;
  action: string;
  actor_role: string;
  actor_id: string;
  details?: string | null;
  created_at: string;
}

export type UserRole = 'RM' | 'Analyst' | 'MLRO' | 'Ops';
