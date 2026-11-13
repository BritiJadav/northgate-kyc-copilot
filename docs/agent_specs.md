# Northgate KYC Copilot — Agent & Engine Specifications

This document defines the formal specifications for all AI agents and deterministic engines within the Northgate KYC Copilot architecture.

---

## Architecture Pattern: "AI Prepares, Human Decides"

```
[Document / Inputs]
       │
       ▼
┌───────────────────────────────┐
│       LLM Agents (Language)   │ ◄─── Extracts facts, classifies, drafts text
└──────────────┬────────────────┘
               │ (Raw Facts & Citations)
               ▼
┌───────────────────────────────┐
│  Deterministic Engines (Math) │ ◄─── NetworkX DAG, vote shares, business calendar
└──────────────┬────────────────┘
               │ (Verified Proposals)
               ▼
┌───────────────────────────────┐
│     Human Review Workspace    │ ◄─── RM reviews draft; Analyst accepts/edits/rejects
└──────────────┬────────────────┘
               │ (Confirmed Only)
               ▼
┌───────────────────────────────┐
│       confirmed_records       │ ◄─── Downstream consumption (Constraint C9)
└───────────────────────────────┘
```

---

## Module A: Document Chaser Agents

### 1. DocClassifierAgent
- **Role**: Extracts observable factual document metadata from uploaded PDFs or image scans.
- **Model**: Google Gemini (`gemini-2.5-flash`), temperature `0.0`.
- **Structured Schema**: `DocClassifierOutput`
  - `doc_type`: String (Passport, Proof of Address, Trust Deed, Certificate of Incorporation, etc.)
  - `party_name`: String (name as written on document)
  - `issue_date`: Optional ISO date (`YYYY-MM-DD`)
  - `expiry_date`: Optional ISO date (`YYYY-MM-DD`)
  - `page_count`: Integer
  - `pages_present`: String (e.g. `"1-2 of 4"`)
  - `signed`: Optional Boolean (`True`, `False`, or `None`)
  - `extracted_fields`: Key-value dictionary of observed fields
- **Constraint C3**: Zero authenticity or forgery judgements. Facts only.

### 2. GapFinderAgent & GapEngine
- **Role**: Evaluates all case parties against the regulatory matrix in a single deterministic pass.
- **Engine**: `backend/app/engines/gap_engine.py` (Deterministic Python, zero LLM calls).
- **Inputs**: Case client type (`individual`, `company`, `trust`), party roster, received documents, simulated date.
- **Outputs**: List of `GapRow` objects with status (`OK`, `MISSING`, `EXPIRED`, `STALE`, `INCOMPLETE`, `WRONG_TYPE`, `UNSIGNED`, `NAME_MISMATCH`), evidence string, and rule ID.
- **Internal Follow-ons**: Derives confidential RM notes (e.g. missing shareholder register may reveal an undisclosed 25%+ owner).

### 3. EmailDrafterAgent
- **Role**: Consolidates all active document gaps across all parties into a single professional, courteous client email.
- **Model**: Google Gemini, temperature `0.0`, prompt `email_drafter_v1.md`.
- **Inputs**: Client name, client type, RM name, list of active gaps, deadline.
- **Outputs**:
  - `subject`: String
  - `body`: Text containing bracketed placeholders `[RM TO CONFIRM: ...]` for ambiguous fields
  - `notes_for_rm`: Strategic advice for the RM
  - `placeholders_count`: Integer
- **Constraint C2**: The email draft is saved with status `draft`. The simulated send button is strictly gated until all placeholders are confirmed.

### 4. GuardrailAgent
- **Role**: Deterministic pre-presentation and pre-send safety barrier.
- **Engine**: `backend/app/agents/guardrail_agent.py`.
- **Automated Checks**:
  1. `forbidden_phrases`: Scans for 16 aggressive/prohibited words (`fraud`, `suspicious`, `penalty`, `freeze`, `criminal`).
  2. `confidential_followon_leakage`: Ensures internal RM notes (e.g. "register may reveal hidden owner") never leak to the client.
  3. `unresolved_placeholders`: Detects regex `\[RM TO CONFIRM:\s*[^\]]+\]`.
  4. `gap_coverage`: Ensures every outstanding document gap is explicitly mentioned.

### 5. FollowUpAgent & Business Calendar
- **Role**: Evaluates follow-up cadence rules based on mock business calendar.
- **Engine**: `backend/app/engines/followup_rules.py` and `business_calendar.py`.
- **Cadence Rules**:
  - **Day 3**: Pre-drafts a gentle reminder email for RM review.
  - **Day 6**: Suggests a phone call and pre-drafts RM talking points.
  - **Day 9**: Escalates to Team Lead / RM Manager and contacts nobody externally.
- **Guardrails**: Max 1 reminder per day; snoozing pauses firing; partial client reply resets the business day clock.

---

## Module B: Analyst Assist Agents & Deterministic Math Engines

### 1. OwnershipExtractorAgent
- **Role**: Extracts ownership edges and share counts from corporate register documents.
- **Model**: Google Gemini, temperature `0.0`, prompt `ownership_extractor_v1.md`.
- **Outputs**: List of direct shareholding edges:
  - `owner`: String (individual or corporate entity)
  - `owned`: String (target or intermediary company)
  - `percentage`: Optional Float
  - `shares_count`: Optional Float
  - `share_class`: String (`Ordinary`, `Class A`, `Class B Preference`)
  - `votes_per_share`: Optional Float
  - `citation`: Verifiable reference (`doc_source`, `page`, `line`, `verbatim_quote`)

### 2. LookthroughEngine (Deterministic Math — Constraint C6)
- **Engine**: `backend/app/engines/lookthrough.py` (NetworkX Directed Acyclic Graph).
- **Zero LLM Arithmetic**: All look-through calculations are computed deterministically.
- **Capabilities**:
  - Path product multiplication: e.g. `(48% x 40%) + (48% x 60% x 50%) = 19.2% + 14.4% = 33.6%`.
  - Multi-tier tree traversal across unlimited holding tiers.
  - Cycle detection using `nx.simple_cycles`.
  - Unresolved percentage aggregation: flags unmasked corporate entities (e.g. Pilar 27% + Meridian 10% = 37% unresolved).

### 3. VoteCalcEngine (Deterministic Math — Constraint C6)
- **Engine**: `backend/app/engines/vote_calc.py`.
- **Dual-Class Voting Rights**:
  - Evaluates disproportionate voting power (e.g. Lumen Growth LP holding 33.3% equity but 83.33% voting power via 10-vote Class B shares).
  - Emits exact formula strings for human verification.

### 4. ControlFlagsAgent
- **Role**: Identifies governance control, nominee arrangements, and fiduciary holdings.
- **Model**: Google Gemini, prompt `control_flags_v1.md`.
- **Flags**:
  - `nominee`: Nominee shareholder with undisclosed beneficial owner (e.g. Meridian Nominees Ltd &rarr; triggers KYC gap).
  - `trustee_without_beneficiaries`: Fiduciary holding shares without declared beneficiaries (e.g. Wren Fiduciary Ltd).
  - `board_control`: Power to appoint majority of the board of directors.
  - `power_of_attorney`: Appointed attorney or authorized signatory.

### 5. EntityResolutionAgent (Constraint C8)
- **Role**: Detects candidate matches across tiers without auto-merging.
- **Model**: Google Gemini, prompt `entity_resolution_v1.md`.
- **Candidate Match Rule**: Matches parties with similar names (e.g. Tomas Berg vs. Thomas Berg) sharing identical date of birth or address.
- **Enforcement**: Prompts the analyst: *"Possible match: confirm or separate?"*
- **Dynamic Recomputation**: The look-through engine recomputes effective ownership only after the analyst confirms the match.

### 6. QuoteVerifier (Constraint C5)
- **Engine**: `backend/app/engines/quote_verifier.py`.
- **Deterministic Citation Verification**:
  - Scans the pre-indexed line text layers of each document.
  - Normalizes whitespace, capitalization, and minor OCR character noise.
  - Validates exact substrings and uses `SequenceMatcher` (threshold `0.75`).
  - Citations failing verification are rejected before the analyst sees them.
