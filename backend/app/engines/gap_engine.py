import re
from datetime import datetime, date
from typing import List, Dict, Any, Tuple, Optional
from backend.app.schemas.common import GapStatusEnum
from backend.app.engines.requirements_matrix import get_required_items_for_case, RequiredItem
from backend.app.engines.business_calendar import parse_date

def calculate_month_difference(d1: date, d2: date) -> int:
    """Computes full months between d1 (earlier) and d2 (later)."""
    return (d2.year - d1.year) * 12 + d2.month - d1.month

def evaluate_document_for_requirement(
    req: RequiredItem,
    doc: Optional[Dict[str, Any]],
    current_date_str: str
) -> Tuple[GapStatusEnum, str]:
    """
    Evaluates a single received document against a requirement item.
    Returns: (GapStatusEnum, evidence_explanation)
    """
    if not doc:
        return GapStatusEnum.MISSING, f"No document provided for {req.requirement}."

    curr_date = parse_date(current_date_str)

    # 1. Check Document Type Match
    doc_type = doc.get("doc_type") or ""
    type_matched = any(
        req_type.lower() in doc_type.lower() or doc_type.lower() in req_type.lower()
        for req_type in req.doc_types
    )
    if not type_matched and doc_type:
        return GapStatusEnum.WRONG_TYPE, f"Received document type '{doc_type}' does not satisfy required '{req.requirement}'."

    # 2. Check Name Match if party is an individual
    doc_party_name = doc.get("party_name") or ""
    if req.party_role not in ["company_entity", "trust"] and doc_party_name:
        req_clean = req.party_name.lower().strip()
        doc_clean = doc_party_name.lower().strip()
        if req_clean not in doc_clean and doc_clean not in req_clean:
            return GapStatusEnum.NAME_MISMATCH, f"Name on document ('{doc_party_name}') does not match party '{req.party_name}'."

    # 3. Check Expiry Date
    if req.must_be_unexpired:
        expiry_str = doc.get("expiry_date")
        if expiry_str:
            try:
                exp_date = parse_date(expiry_str)
                if exp_date < curr_date:
                    return GapStatusEnum.EXPIRED, f"Document expired on {expiry_str} (as of current verification date {current_date_str})."
            except Exception:
                pass

    # 4. Check Staleness / Max Age (e.g. Proof of Address max 3 months)
    if req.max_age_months is not None:
        issue_str = doc.get("issue_date")
        if issue_str:
            try:
                iss_date = parse_date(issue_str)
                # Compute difference in months
                months_diff = calculate_month_difference(iss_date, curr_date)
                if months_diff > req.max_age_months:
                    return (
                        GapStatusEnum.STALE,
                        f"Document dated {issue_str} is {months_diff} months old (exceeds maximum allowed {req.max_age_months} months)."
                    )
            except Exception:
                pass

    # 5. Check Completeness (pages present)
    pages_present = doc.get("pages_present") or ""
    # Check patterns like "1-2 of 4", "1-11 of 12"
    match = re.search(r"(\d+)\s*(?:-|to)\s*(\d+)\s+of\s+(\d+)", pages_present, re.IGNORECASE)
    if match:
        start_p, end_p, total_p = int(match.group(1)), int(match.group(2)), int(match.group(3))
        if end_p < total_p:
            missing_pages = f"{end_p + 1}-{total_p}" if end_p + 1 < total_p else f"{total_p}"
            return (
                GapStatusEnum.INCOMPLETE,
                f"Document is incomplete: pages {pages_present} received (missing page(s) {missing_pages})."
            )

    # 6. Check Signed if mandatory
    if req.must_be_signed:
        signed_val = doc.get("signed")
        if signed_val is False:
            return GapStatusEnum.UNSIGNED, f"Document requires an authorized signature but was submitted unsigned."

    return GapStatusEnum.OK, f"Document meets all validation criteria ({doc.get('filename')})."

def run_gap_engine(
    client_type: str,
    parties: List[Dict[str, Any]],
    documents: List[Dict[str, Any]],
    current_date_str: str
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    Runs deterministic single-pass gap analysis for a case.
    Returns: (list_of_gap_rows, possible_followons)
    """
    required_items = get_required_items_for_case(client_type, parties)
    gap_rows = []

    for req in required_items:
        # Find best candidate document among received documents
        matching_doc = None
        for doc in documents:
            doc_type = doc.get("doc_type") or ""
            doc_party = (doc.get("party_name") or "").lower()
            req_party = req.party_name.lower()

            # Does doc match type?
            type_match = any(t.lower() in doc_type.lower() for t in req.doc_types)
            
            # For corporate/trust docs, type match is sufficient
            if req.party_role in ["company_entity", "trust"]:
                if type_match:
                    matching_doc = doc
                    break
            else:
                # For individuals, match both party name and type
                if type_match and (req_party in doc_party or doc_party in req_party or not doc_party):
                    matching_doc = doc
                    break

        status, evidence = evaluate_document_for_requirement(req, matching_doc, current_date_str)

        gap_rows.append({
            "party_name": req.party_name,
            "party_role": req.party_role,
            "requirement": req.requirement,
            "status": status.value,
            "evidence": evidence,
            "rule_id": req.rule_id,
            "is_active": (status != GapStatusEnum.OK),
            "filename": matching_doc.get("filename") if matching_doc else None,
        })

    # Derive possible follow-ons (RM-only)
    possible_followons = None
    if client_type == "company":
        reg_gap = next((g for g in gap_rows if g["rule_id"] == "REQ-CORP-01" and g["status"] != "OK"), None)
        if reg_gap:
            possible_followons = "Shareholder register may reveal an additional beneficial owner holding >= 25% voting or equity interest."
    elif client_type == "trust":
        deed_gap = next((g for g in gap_rows if g["rule_id"] == "REQ-TRST-01" and g["status"] != "OK"), None)
        if deed_gap:
            possible_followons = "Once complete execution page of trust deed is received, confirm if protector or named beneficiaries have vested rights."

    return gap_rows, possible_followons
