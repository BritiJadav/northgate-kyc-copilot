# Northgate KYC Copilot — Honest Technical Limitations & Scope Boundaries

In production-grade applied AI for financial compliance, knowing what an AI system does **NOT** do is as important as knowing what it can do. This document transparently records the design boundaries, known edge cases, and scope limitations of the Northgate KYC Copilot.

---

## 1. Non-Validated Document Conditions (Constraint C3)

### 1.1 Authenticity & Forensic Forgery Analysis
- **Limitation**: The system does **not** judge whether a passport, utility bill, or corporate certificate is genuine, manipulated, or counterfeit.
- **Rationale**: LLMs and standard OCR tools are unsuited for forensic pixel analysis, UV watermark verification, microprint validation, or MRZ cryptographic checksums.
- **System Behavior**: The system validates only observable, factual attributes:
  - Document presence and type
  - Text-based issue and expiry dates
  - Page completeness (e.g. pages 1–2 of 4)
  - Signature line presence (signed vs unsigned)
  - Name consistency between document text and case parties

### 1.2 Handwritten Cursive & Severe Degradation
- **Limitation**: While low-legibility and skewed scans (e.g. `calder_stock_transfer_scan.png`) are supported through image inspection and fuzzy Levenshtein matching, deeply degraded handwritten cursive signatures and notes are not guaranteed to be decoded accurately.
- **Mitigation**: When confidence falls below 75% or citations cannot be matched against document text layers, the system outputs `NOT_FOUND` and prompts the human analyst to review the physical file.

---

## 2. Regulatory & Legal Boundaries (Constraint C4 & C6)

### 2.1 Zero Risk Rating / Scoring (MLRO Red Line)
- **Limitation**: The copilot will **never** output a risk score (e.g. "Score: 78/100"), risk band ("Medium Risk"), color ("Amber"), or automated decision flag ("Suspicious").
- **Rationale**: Northgate's Money Laundering Reporting Officer (MLRO) and regulatory rules mandate that risk classification is an exclusively human, legally accountable decision.
- **System Behavior**: The system supplies verified facts (e.g. "Holds 83.3% voting power via Class B shares", "Missing execution page 12 of Trust Deed"). The human analyst and MLRO determine the final risk rating.

### 2.2 Discretionary Trust Vesting & Tax Treaties
- **Limitation**: In trust structures (such as `Okafor Family Trust` or `Rowan Bay Consulting Ltd`), the system detects settlors, trustees, and named beneficiaries. However, it does not interpret complex trust law nuances, such as discretionary powers of appointment, contingent remainders, or double-taxation treaty eligibility.
- **Mitigation**: The system flags trusts as requiring full deed verification and notes potential follow-ons for the Relationship Manager.

---

## 3. Operational & Network Boundaries (Constraint C2 & C9)

### 3.1 Simulated Outbox Only (No Real Email Transmission)
- **Limitation**: Under Constraint C2, nothing leaves the system. Emails drafted by the system are stored in `chase_emails` (with status `sent_simulated`) only after an RM explicitly clicks the Send button.
- **Mitigation**: Northgate's production IT will connect the confirmed outbox to an authorized exchange connector only after pilot approval.

### 3.2 Downstream Data Separation (Constraint C9)
- **Limitation**: Downstream systems (core banking, loan origination, CRM) are strictly prohibited from reading `ai_suggestions`.
- **System Behavior**: Downstream consumers read exclusively from `confirmed_records`, which are populated only when a human analyst accepts, edits, or adds fields. If an analyst rejects a suggestion, it never reaches downstream systems.

---

## 4. Multi-Language & Multi-Jurisdictional Scope

### 4.1 Non-English Primary Filings
- **Limitation**: The current system is optimized for English-language company registers (UK Companies House, Jersey, BVI, Isle of Man). While it recognizes common multilingual entity suffixes (`S.A.`, `B.V.`, `GmbH`, `LLC`, `LP`) and basic foreign registers (e.g. French incumbency papers in `norvik_group_register_fr.pdf`), it does not replace sworn legal translations required for official court filings.

### 4.2 Sanctions & PEP Screening
- **Limitation**: Screening against OFSI, OFAC, and UN sanctions lists is handled by Northgate's dedicated core screening engine. Document Chaser and Analyst Assist do not perform live PEP/sanctions watch-list API calls.
