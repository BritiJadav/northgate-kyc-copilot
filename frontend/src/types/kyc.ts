export interface CompanyDocument {
  id: number;
  company_id: number;
  filename: string;
  file_path: string;
  doc_hash: string;
  page_count: number;
  low_legibility: boolean;
  created_at: string;
}

export interface AISuggestionItem {
  id: number;
  company_id: number;
  field_name: string;
  value: string;
  field_type: 'EXTRACTED' | 'COMPUTED' | 'NOT_FOUND';
  formula?: string | null;
  confidence: number;
  doc_source?: string | null;
  page?: number | null;
  line?: number | null;
  verbatim_quote?: string | null;
  citation_verified: boolean;
  as_at: string;
  has_decision: boolean;
  decision?: {
    action: 'accept' | 'edit' | 'reject' | 'add';
    final_value: string;
    reason_code?: string | null;
    rationale?: string | null;
    analyst_id: string;
  } | null;
}

export interface PossibleMatchItem {
  id: number;
  person_a_name: string;
  person_b_name: string;
  person_a_dob?: string | null;
  person_b_dob?: string | null;
  reason: string;
  status: 'pending' | 'confirmed_same' | 'confirmed_different';
}

export interface CompanySummary {
  id: number;
  name: string;
  code: string;
  jurisdiction: string;
  registration_number: string;
  incorporation_date?: string | null;
  status: string;
  pending_decisions_count: number;
}

export interface ConfirmedRecord {
  id: number;
  company_id: number;
  field_name: string;
  value: string;
  field_type: string;
  formula?: string | null;
  source_citation?: string | null;
  confirmed_by: string;
  as_at: string;
  created_at: string;
}

export interface GraphNode {
  id: string;
  label: string;
  type: 'target' | 'entity' | 'person';
}

export interface GraphEdge {
  source: string;
  target: string;
  percentage: number;
  label: string;
}

