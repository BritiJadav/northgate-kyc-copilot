# Northgate KYC Copilot — Technical Architecture

This document describes the end-to-end architecture, database schema, data separation boundaries, and hard constraint mappings of the **Northgate KYC Copilot**.

---

## 1. System Overview

```
                      ┌───────────────────────────────────────────┐
                      │        React 18 + Vite + Tailwind         │
                      │  (RM Workspace, Split-Review, Analytics)  │
                      └─────────────────────┬─────────────────────┘
                                            │ HTTP / JSON
                                            ▼
                      ┌───────────────────────────────────────────┐
                      │              FastAPI Backend              │
                      │  - /api/cases, /api/chase, /api/companies │
                      │  - /api/analyst, /api/metrics, /governance│
                      └─────────────┬───────────────┬─────────────┘
                                    │               │
                    ┌───────────────┴────┐     ┌────┴────────────────┐
                    │ Deterministic Core │     │   LLM Agent Core    │
                    │ - Requirements Mat │     │ - DocClassifier     │
                    │ - Gap Engine       │     │ - EmailDrafter      │
                    │ - NetworkX Lookthr │     │ - OwnershipExtract  │
                    │ - Vote Calculation │     │ - ControlFlags      │
                    │ - Quote Verifier   │     │ - EntityResolution  │
                    │ - BusinessCalendar │     │ - Guardrail Agent   │
                    └───────────────┬────┘     └────┬────────────────┘
                                    │               │
                                    ▼               ▼
                      ┌───────────────────────────────────────────┐
                      │             SQLite Database               │
                      │  - Module A: chase_cases, gap_rows, emails│
                      │  - Module B: ai_suggestions (ISOLATED)    │
                      │  - Final:    confirmed_records (DOWNSTRM) │
                      └───────────────────────────────────────────┘
```

---

## 2. Hard Constraints Mapping Matrix (C1 – C12)

Every hard constraint is mapped to its implementing code, database model, and automated test:

| ID | Constraint Requirement | Implementation File | Verification Test |
|---|---|---|---|
| **C1** | Official `google-genai` Python SDK, `temperature=0`, JSON structured schema | `backend/app/llm/client.py` | `test_llm_client_demo_cache_resilience` |
| **C2** | Zero auto-send; simulated outbox only after explicit RM click | `backend/app/routers/cases.py`<br>`backend/app/agents/guardrail_agent.py` | `test_constraint_c2_cannot_send_with_unresolved_placeholders` |
| **C3** | Observable facts only; zero forgery or authenticity judgements | `backend/app/engines/gap_engine.py` | `test_every_gap_status_type` |
| **C4** | Zero risk ratings, scores, bands, or "suspicious" flags (MLRO Red Line) | `backend/app/models/`<br>`backend/app/routers/governance.py` | `test_hard_constraint_c4_no_risk_columns` |
| **C5** | Verifiable citations (`doc, page, line, quote`) with deterministic verification | `backend/app/engines/quote_verifier.py` | `test_quote_verifier_exact_match`<br>`test_quote_verifier_rejects_fabricated_quote` |
| **C6** | All arithmetic computed deterministically (Python/NetworkX, no LLM math) | `backend/app/engines/lookthrough.py`<br>`backend/app/engines/vote_calc.py` | `test_vote_calc.py`<br>`test_lookthrough.py` |
| **C7** | Strict field types: `EXTRACTED`, `COMPUTED`, or `NOT_FOUND` (no "inferred") | `backend/app/schemas/common.py`<br>`backend/app/models/kyc.py` | `test_confirm_workflow_and_c9.py` |
| **C8** | Entity resolution requires explicit human confirmation (no auto-merge) | `backend/app/agents/entity_resolution_agent.py`<br>`backend/app/routers/analyst.py` | `test_kestrel_entity_resolution_and_submission_workflow` |
| **C9** | Strict data separation (`ai_suggestions` vs `confirmed_records`) | `backend/app/services/confirm_workflow.py`<br>`backend/app/routers/governance.py` | `test_hard_constraint_c9_strict_data_separation` |
| **C10** | Seeded canaries in pilot mode to track analyst vigilance (hidden in UI) | `backend/app/services/confirm_workflow.py`<br>`backend/app/routers/metrics.py` | `test_hard_constraint_c10_canaries` |
| **C11** | 100% synthetic data with prominent UI banner | `frontend/src/components/Banner.tsx`<br>`backend/app/seed/seed_data.py` | `test_data_generation_and_seeding` |
| **C12** | Offline demo resilience: pre-recorded responses in `demo_cache/` | `backend/app/llm/client.py`<br>`scripts/record_demo_cache.py` | `test_llm_client_demo_cache_resilience` |

---

## 3. Data Separation Architecture (Constraint C9)

```
                    ┌───────────────────────────────┐
                    │       Gemini AI Extract       │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │        ai_suggestions         │
                    │ - value: "33.6%"              │
                    │ - canary_flag: True/False     │
                    │ - citation_verified: True     │
                    │ (STRICTLY INTERNAL TO PILOT)  │
                    └───────────────┬───────────────┘
                                    │
                     Human Decision: Accept / Edit / Reject
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │       confirmed_records       │
                    │ - value: "33.6%"              │
                    │ - confirmed_by: "analyst_1"   │
                    │ - timestamp: 2026-11-12...    │
                    │ (READ-ONLY AUDITOR LEDGER)    │
                    └───────────────┬───────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │ Downstream Core Banking / API │
                    └───────────────────────────────┘
```

Downstream systems (core banking, credit committee, account opening) have zero read permission on `ai_suggestions`. All downstream queries, reports, and export endpoints read exclusively from `confirmed_records`.

---

## 4. Deterministic Engines

### 4.1 Requirements Matrix & Gap Engine
- Rules matrix defines document requirements based on client type (`individual`, `company`, `trust`) and party roles (`director`, `owner_25_plus`, `trustee`, `settlor`).
- Single pass evaluates all received documents against:
  - Document type matching
  - Party name alignment
  - Expiry date verification
  - Staleness limit (e.g. proof of address max 3 months)
  - Page completeness (e.g. "1-2 of 4 received")
  - Authorized signature presence

### 4.2 Look-Through Ownership Graph (NetworkX)
- Represents corporate hierarchies as directed graphs (DAGs).
- Computes multi-path cumulative products:
  $$\text{Effective \%} = \sum_{\text{paths}} \prod_{e \in \text{path}} w_e$$
- Identifies cycles (`nx.simple_cycles`) without crashing or infinite recursion.
- Aggregates unresolved institutional shareholdings (e.g. nominee and trustee companies).

### 4.3 Voting Rights Calculation
- Dual-class share capital calculation:
  $$\text{Vote \%} = \frac{\text{Shares} \times \text{Votes per Share}}{\sum (\text{Shares} \times \text{Votes per Share})}$$
- Highlights discrepancies where voting control significantly diverges from equity ownership (e.g. Lumen Growth LP 33.3% equity vs. 83.33% voting power).
