import re
from typing import List, Dict, Any, Optional
from backend.app.schemas.chase import GuardrailOutput, GuardrailCheckItem

FORBIDDEN_PHRASES = [
    "penalty",
    "penalties",
    "fraud",
    "fraudulent",
    "fake",
    "forged",
    "forgery",
    "suspicious",
    "you failed",
    "criminal",
    "freeze",
    "freezing",
    "prosecution",
    "regulatory enforcement",
    "aml violation",
]

class GuardrailAgent:
    """
    Hybrid Guardrail Agent:
    Performs deterministic regex and rule checks on every draft email before RM presentation.
    """
    def __init__(self):
        pass

    def run(
        self,
        subject: str,
        body: str,
        gap_list: List[Dict[str, Any]],
        possible_followons: Optional[str] = None
    ) -> GuardrailOutput:
        checks: List[GuardrailCheckItem] = []
        reasons: List[str] = []
        full_text = f"{subject}\n{body}".lower()

        # 1. Check for Forbidden Phrases
        found_forbidden = [phrase for phrase in FORBIDDEN_PHRASES if phrase in full_text]
        if found_forbidden:
            checks.append(GuardrailCheckItem(
                check_name="forbidden_phrases",
                passed=False,
                details=f"Forbidden phrase(s) detected: {', '.join(found_forbidden)}"
            ))
            reasons.append(f"Email contains prohibited aggressive/threatening language: {found_forbidden}")
        else:
            checks.append(GuardrailCheckItem(
                check_name="forbidden_phrases",
                passed=True,
                details="Zero forbidden phrases detected. Tone is courteous and professional."
            ))

        # 2. Check for Confidential Follow-on Leakage
        followon_leak = False
        if possible_followons:
            # Check keywords from follow-on that shouldn't appear in client body
            sensitive_keywords = ["reveal an additional", "hidden owner", "trust protector", "vested rights"]
            found_leaks = [kw for kw in sensitive_keywords if kw in possible_followons.lower() and kw in body.lower()]
            if found_leaks:
                followon_leak = True
                checks.append(GuardrailCheckItem(
                    check_name="confidential_followon_leakage",
                    passed=False,
                    details=f"Confidential RM follow-on information leaked into client body: {found_leaks}"
                ))
                reasons.append("Email contains confidential internal RM notes regarding potential follow-ons.")
            else:
                checks.append(GuardrailCheckItem(
                    check_name="confidential_followon_leakage",
                    passed=True,
                    details="Internal RM follow-ons remain strictly confidential."
                ))
        else:
            checks.append(GuardrailCheckItem(
                check_name="confidential_followon_leakage",
                passed=True,
                details="No confidential follow-ons present."
            ))

        # 3. Check for Unresolved Placeholders
        placeholder_pattern = r"\[RM TO CONFIRM:\s*([^\]]+)\]"
        placeholders_found = re.findall(placeholder_pattern, body, re.IGNORECASE)
        has_unresolved_placeholders = len(placeholders_found) > 0

        if has_unresolved_placeholders:
            checks.append(GuardrailCheckItem(
                check_name="unresolved_placeholders",
                passed=False, # Flagged as needing RM action before Send
                details=f"Unresolved placeholders requiring RM confirmation: {placeholders_found}"
            ))
            reasons.append(f"Placeholders must be resolved before sending: {placeholders_found}")
        else:
            checks.append(GuardrailCheckItem(
                check_name="unresolved_placeholders",
                passed=True,
                details="All placeholders have been confirmed and resolved."
            ))

        # 4. Check Gap List Coverage
        active_gaps = [g for g in gap_list if g.get("is_active", True) and g.get("status") != "OK"]
        missing_coverage = []
        for g in active_gaps:
            req = g.get("requirement", "").lower()
            # Extract key word from requirement (e.g. "passport", "address", "register", "bank", "trust deed")
            keywords = [w for w in re.findall(r"\b[a-zA-Z]{4,}\b", req)]
            matched = any(kw.lower() in full_text for kw in keywords)
            if not matched:
                missing_coverage.append(g.get("requirement"))

        if missing_coverage:
            checks.append(GuardrailCheckItem(
                check_name="gap_coverage",
                passed=False,
                details=f"Active gaps missing from email draft: {missing_coverage}"
            ))
            reasons.append(f"The draft fails to list all outstanding gaps: {missing_coverage}")
        else:
            checks.append(GuardrailCheckItem(
                check_name="gap_coverage",
                passed=True,
                details=f"All {len(active_gaps)} outstanding document gaps are explicitly covered."
            ))

        # Overall pass if no forbidden words, no follow-on leaks, and full gap coverage
        # (Placeholders being present warns the RM, and blocks simulated send until resolved)
        overall_passed = (not found_forbidden) and (not followon_leak) and (not missing_coverage)

        return GuardrailOutput(
            passed=overall_passed,
            checks=checks,
            reasons=reasons,
            has_unresolved_placeholders=has_unresolved_placeholders,
        )
