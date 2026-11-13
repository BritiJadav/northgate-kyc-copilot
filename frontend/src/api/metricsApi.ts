import { apiFetch } from './client';

export interface OnboardingStageBreakdown {
  stage: string;
  baseline_days: number;
  copilot_days: number;
  days_saved: number;
}

export interface MetricsSummaryResponse {
  disclaimer: string;
  onboarding_time_reduction: {
    baseline_days: number;
    copilot_target_days: number;
    days_saved: number;
    percent_reduction: number;
    breakdown: OnboardingStageBreakdown[];
  };
  module_a: {
    name: string;
    cycle_time: {
      baseline_days: number;
      copilot_days: number;
      improvement_factor: string;
    };
    chase_rounds: {
      baseline_avg: number;
      copilot_avg: number;
      rounds_reduction_pct: number;
    };
    telemetry: {
      active_cases: number;
      simulated_outbox_sent: number;
      rm_edit_rate_pct: number;
    };
  };
  module_b: {
    name: string;
    review_time: {
      baseline_hours_per_file: number;
      copilot_minutes_per_file: number;
      improvement_factor: string;
    };
    decisions: {
      total_suggestions: number;
      total_decisions: number;
      accept_count: number;
      edit_count: number;
      reject_count: number;
      accept_rate_pct: number;
      edit_rate_pct: number;
      reject_rate_pct: number;
    };
    field_types: {
      EXTRACTED: number;
      COMPUTED: number;
      NOT_FOUND: number;
    };
    canary_monitoring: {
      canaries_planted: number;
      canaries_caught: number;
      canaries_missed: number;
      canary_catch_rate_pct: number;
      silent_wrong_rate_pct: number;
      analyst_vigilance_status: string;
    };
    governance: {
      confirmed_records_count: number;
    };
  };
}

export const metricsApi = {
  getSummary: () => apiFetch<MetricsSummaryResponse>('/api/metrics/summary'),
};
