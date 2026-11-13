# Northgate KYC Copilot — 10-Minute Guide Walkthrough Script

This script is structured for a Forward Deployed Engineer (FDE) presenting the **Northgate KYC Copilot** to their engineering guide/mentor.

---

## 0. Executive Hook & Context (0:00 - 1:30)

**Talking Points:**
> "Northgate's client onboarding currently averages **62 days per case**. When we profiled the pipeline, two bottlenecks accounted for nearly half of the delay:
> 1. **Module A: Document Chaser (17 of 62 days)** — Gaps are discovered piecemeal in 3 sequential rounds of 5–6 days. We replace this with a deterministic single-pass gap engine, consolidated email drafting, pre-send guardrails, and automated Day 3/6/9 reminder cadence.
> 2. **Module B: Analyst Assist (11 of 62 days)** — Analysts spend days tracing multi-tier corporate hierarchies and voting rights from incorporation documents. We pre-fill owners, percentages, voting rights, and look-through with exact line citations, while enforcing strict human confirmation.
>
> **Core Design Principle**: *'AI prepares, human decides.'* Nothing is auto-sent. Nothing is auto-accepted. The AI never outputs risk scores or bands."

**Where to show the Guide:**
- Open `http://localhost:3000` (Home page).
- Point to the **62-Day Bottleneck Waterfall Bar** (`17d Chaser + 11d Analyst + 34d Other Operations`).
- Point to the **"SYNTHETIC DEMO DATA"** top banner (Constraint C11).

---

## 1. Module A: Document Chaser (1:30 - 4:00)

### Step 1.1: Single-Pass Gap Detection (Case 2 - Harbourline Logistics Ltd)
**Action:** Click **"Document Chaser"** in the top navigation or click **"Open Chaser"** on Case 2 (`CASE-2026-002`).

**Talking Points:**
> "Under the legacy process, Marcus (the RM) asked for the Certificate of Incorporation, waited 5 days, found out the bank statement was missing pages, waited another 5 days, and then realized 2 beneficial owners were missing passports.
> Watch how our deterministic rules engine evaluates all parties in a **single pass**."

**Show in UI:**
- Look at the **Document Requirements Matrix**.
- Point out the statuses:
  - `Harbourline Logistics Ltd` &rarr; Bank Statement: `INCOMPLETE` (Pages 1–2 of 4 received).
  - `Daniel Whitaker` (40% owner) &rarr; Passport: `MISSING`, Proof of Address: `MISSING`.
  - `Alicia Moreno` (30% owner) &rarr; Passport: `MISSING`, Proof of Address: `MISSING`.
- Toggle a gap row off and on, or click **"Add Requirement"** to demonstrate RM override.
- Click **"View Audit Trail"** to show immutable logging of RM actions.

**Show in Code:**
- Open `backend/app/engines/gap_engine.py` &rarr; show `run_gap_engine`: pure deterministic Python rules, zero LLM hallucinations.

---

### Step 1.2: AI Email Draft & Guardrails (Constraint C2)
**Action:** Look at the middle column: **Consolidated Client Email Draft**.

**Talking Points:**
> "The LLM synthesized all 6 outstanding gaps across all parties into **ONE courteous email**.
> Notice the highlighted placeholder: `[RM TO CONFIRM: preferred secondary signatory]`.
> Notice that the **Send Email** button is completely disabled (Constraint C2). It will not allow transmission until Marcus confirms every bracketed item."

**Action:**
1. Try clicking **"Simulate Send"** &rarr; alert blocks it.
2. Replace `[RM TO CONFIRM: preferred secondary signatory]` with `Daniel Whitaker`.
3. The guardrails card turns green: `All placeholders resolved`.
4. Click **"Simulate Send to Outbox"** &rarr; toast confirms write to simulated outbox. Nothing ever leaves the firm.

**Show in Code:**
- Open `backend/app/agents/guardrail_agent.py` &rarr; show regex check for `[RM TO CONFIRM: ...]` and check preventing internal follow-on leakage.

---

### Step 1.3: Cadence Reminders & Mock Clock (Case 3 - Okafor Family Trust)
**Action:**
1. Point to **Okafor Family Trust** on the dashboard. Last contact date: `2026-11-09` (3 business days ago relative to clock base date `2026-11-12`).
2. Click **"RM Tasks"** in navigation.
3. Show the **Day 3 Gentle Follow-up** task pre-drafted.
4. Click **"+3 Days"** in the top clock navigation bar &rarr; clock advances to `2026-11-17` (skipping weekend!).
5. Show how the Day 6 task (suggesting phone call) triggers, and Day 9 flags the Team Lead.

**Show in Code:**
- Open `backend/app/engines/business_calendar.py` &rarr; show weekend skipping logic and `is_business_day`.
- Open `backend/app/engines/followup_rules.py` &rarr; show Day 3/6/9 deterministic trigger matrix.

---

## 2. Module B: Analyst Assist & Split-Review Workspace (4:00 - 7:30)

### Step 2.1: Company B (Brightwave Software Ltd) — Dual-Class Voting Disparity (Constraint C6)
**Action:** Click **"Analyst Assist"** &rarr; Select **Brightwave Software Ltd** (`/analyst/2`).

**Talking Points:**
> "Brightwave has 2 share classes: Class A (1 vote/share) and Class B (10 votes/share).
> Ines Duarte holds 40% of the equity, but only 10% of the voting power.
> Lumen Growth LP holds 33.3% equity, but **83.33% of the voting control**!
> Under Constraint C6, this math was computed deterministically by Python, not guessed by an LLM."

**Show in UI:**
- Point to the formula string: `(500 shares x 10 votes) / 6000 total votes = 83.33%`.
- Click **"View Ownership Graph"** to reveal the interactive NetworkX structure.

---

### Step 2.2: Company C (Calder Marine) — Low Legibility Skewed Scan & Citations (Constraint C5)
**Action:** Navigate to **Calder Marine Services Ltd** (`/analyst/3`).

**Talking Points:**
> "Calder provided a stale 2023 register (Lars 75%, Maya 25%), but also provided a skewed, rotated transfer sheet image showing a transfer of 60 shares in August 2025.
> Notice the split screen: on the right, Maya is suggested at 55% and Lars at 45%.
> On the left, we can toggle between the line-indexed text reader and the actual skewed scan image (`calder_stock_transfer_scan.png`)."

**Action:**
- In the right column, click the blue citation: `[Doc: calder_stock_transfer_scan.png, P.1, L.6]`.
- The left document viewer instantly scrolls and highlights the cited line and verbatim quote!

**Show in Code:**
- Open `backend/app/engines/quote_verifier.py` &rarr; show whitespace normalization and fuzzy Levenshtein/SequenceMatcher verification.

---

### Step 2.3: Company E (Kestrel Trading Ltd) — Candidate Match & 3 Failure Modes (Constraint C8 & C9)
**Action:** Navigate to **Kestrel Trading Ltd** (`/analyst/5`).

**Talking Points:**
> "Kestrel is a 4-tier holding chain (Kestrel &rarr; Halden &rarr; Norvik).
> Here we showcase our answers to the **3 classic LLM failure modes**:
> 1. **The Berg Split**: In Tier 2, we have *Tomas Berg* (40%). In Tier 3, we have *Thomas Berg* (50%). Before resolution, both hold < 25% look-through. The system does NOT auto-merge them (Constraint C8). Instead, it presents a candidate match card.
> 2. **Nominee Dropping**: Meridian Nominees holds 10%. It is flagged with a nominee requirement and unmasked owner gap, NOT dropped.
> 3. **Trustee as UBO**: Wren Fiduciary Ltd holds 27% as trustee. It is classified as an institutional trustee holding, NOT a natural person UBO."

**Action:**
1. Show the yellow **Entity Resolution Candidate Card**: `"Tomas Berg vs Thomas Berg (DOB: 02/04/1968)"`.
2. Click **"Confirm Same Person"**.
3. Watch the look-through ownership dynamically recompute: Tomas Berg becomes **33.6% UBO** (`(48% x 40%) + (48% x 60% x 50%) = 19.2% + 14.4% = 33.6%`).
4. Review rows: Accept Evelyn/Tomas, Edit or Reject one field with reason code `wrong_value`.
5. Point out that the **"Submit Confirmed KYC File"** button becomes active only after every row is decided (no accept-all!).
6. Click **"Submit Confirmed KYC File"**.

---

## 3. Governance, Live Tripwires & Metrics (7:30 - 9:30)

### Step 3.1: Live Tripwire Verification (Constraint C4 & C9)
**Action:** Click **"Governance"** in navigation (`/governance`).

**Talking Points:**
> "Here is our MLRO compliance shield. Every hard constraint has an automated live tripwire:
> - **C4 MLRO Red Line**: A live query scans all tables in the SQLite database to prove zero risk rating columns exist.
> - **C9 Data Separation**: Downstream banking systems read exclusively from `confirmed_records`. AI suggestions in `ai_suggestions` are physically isolated.
> - **Pilot Operating Mode Switch**: We can toggle between *Assisted Pilot Mode* and *Shadow Mode* with one click."

**Action:**
- Show the 12 green checkmarks.
- Click **"Export CSV"** and **"Export JSON"** to demonstrate auditor-ready output from `confirmed_records`.

---

### Step 3.2: Evaluation Harness & Answer Keys
**Action:** Click **"Eval"** in navigation (`/eval`).

**Talking Points:**
> "Every capability is continuously evaluated against ground-truth answer keys:
> - Module A Gap Discovery: **100% F1 score** across all 3 cases.
> - Module A Guardrails: **100% adversarial rejection rate**.
> - Module B Corporate Trees: **5 of 5 companies passed**.
> - Kestrel Failure Modes: **3 of 3 passed**."

**Action:** Click **"Re-Run Evaluation Harness"** &rarr; executes in ~0.02s and confirms fresh pass status.

---

### Step 3.3: Metrics Dashboard
**Action:** Click **"Metrics"** in navigation (`/metrics`).

**Talking Points:**
> "Here is the ROI for the Northgate executive committee:
> - Overall onboarding: **62 days down to 34 days** (-45.2% cycle reduction).
> - Document chaser: **17 days down to 1 day** (17x acceleration).
> - Chase rounds: **3.2 rounds down to 1.0 round** (-68.8% piecemeal chases).
> - Analyst review: **88 hours down to 22.5 minutes** (230x acceleration).
> - Canary Catch Rate: **92%+ analyst vigilance** tracked via planted errors."

---

## 4. Closing & Q&A (9:30 - 10:00)

**Summary Pitch:**
> "Northgate KYC Copilot demonstrates that in high-stakes financial operations, the winning design is not an autonomous black-box agent, but a precision copilot:
> **Deterministic engines do the math and rule enforcement. LLMs do the reading and drafting. Humans make 100% of the decisions.**"
