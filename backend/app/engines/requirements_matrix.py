from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class RequiredItem(BaseModel):
    rule_id: str
    party_name: str
    party_role: str
    requirement: str
    doc_types: List[str]
    max_age_months: Optional[int] = None
    must_be_unexpired: bool = False
    must_be_complete: bool = True
    must_be_signed: bool = False
    description: str

def get_required_items_for_case(client_type: str, parties: List[Dict[str, Any]]) -> List[RequiredItem]:
    """
    Deterministic rule engine: generates the exact list of requirements
    by expanding requirements across all identified parties (directors, owners >=25%, trustees).
    """
    items: List[RequiredItem] = []

    # 1. Individual Client rules
    if client_type == "individual":
        for party in parties:
            if party.get("role") in ["individual_client", "individual"]:
                name = party["name"]
                items.append(RequiredItem(
                    rule_id="REQ-IND-01",
                    party_name=name,
                    party_role="individual_client",
                    requirement="Passport / National ID",
                    doc_types=["Passport", "National ID", "Driver License"],
                    must_be_unexpired=True,
                    must_be_complete=True,
                    must_be_signed=True,
                    description="Valid unexpired government-issued photo identity document.",
                ))
                items.append(RequiredItem(
                    rule_id="REQ-IND-02",
                    party_name=name,
                    party_role="individual_client",
                    requirement="Proof of Address",
                    doc_types=["Proof of Address", "Utility Bill", "Bank Statement"],
                    max_age_months=3,
                    must_be_unexpired=False,
                    must_be_complete=True,
                    must_be_signed=False,
                    description="Proof of residential address dated within the last 3 months.",
                ))
                items.append(RequiredItem(
                    rule_id="REQ-IND-03",
                    party_name=name,
                    party_role="individual_client",
                    requirement="Source of Funds Declaration",
                    doc_types=["Source of Funds Declaration", "Source of Wealth"],
                    max_age_months=12,
                    must_be_unexpired=False,
                    must_be_complete=True,
                    must_be_signed=True,
                    description="Signed source of funds and wealth declaration.",
                ))

    # 2. Company Client rules
    elif client_type == "company":
        # Corporate entity documents
        company_party = next((p for p in parties if p.get("role") == "company_entity"), None)
        entity_name = company_party["name"] if company_party else "Company Entity"

        items.append(RequiredItem(
            rule_id="REQ-CORP-01",
            party_name=entity_name,
            party_role="company_entity",
            requirement="Register of Members (Shareholders)",
            doc_types=["Register of Members", "Shareholder Register"],
            must_be_unexpired=False,
            must_be_complete=True,
            must_be_signed=True,
            description="Certified register of shareholders detailing all holdings.",
        ))
        items.append(RequiredItem(
            rule_id="REQ-CORP-02",
            party_name=entity_name,
            party_role="company_entity",
            requirement="Certificate of Incorporation",
            doc_types=["Certificate of Incorporation", "Certificate of Good Standing"],
            must_be_unexpired=False,
            must_be_complete=True,
            must_be_signed=False,
            description="Official Certificate of Incorporation from Registrar of Companies.",
        ))
        items.append(RequiredItem(
            rule_id="REQ-CORP-04",
            party_name=entity_name,
            party_role="company_entity",
            requirement="Bank Statement",
            doc_types=["Bank Statement"],
            max_age_months=3,
            must_be_unexpired=False,
            must_be_complete=True,
            must_be_signed=False,
            description="Bank statement for the most recent period; all pages required.",
        ))

        # Beneficial Owners (>= 25%) rules
        for p in parties:
            role = p.get("role")
            pct = p.get("ownership_pct") or 0.0
            if role == "owner_25_plus" or (pct >= 25.0 and role != "company_entity"):
                name = p["name"]
                items.append(RequiredItem(
                    rule_id="REQ-UBO-01",
                    party_name=name,
                    party_role="owner_25_plus",
                    requirement="Passport / Photo ID",
                    doc_types=["Passport", "National ID"],
                    must_be_unexpired=True,
                    must_be_complete=True,
                    must_be_signed=False,
                    description=f"Passport or Photo ID for {name} ({pct:.0f}% owner).",
                ))
                items.append(RequiredItem(
                    rule_id="REQ-UBO-02",
                    party_name=name,
                    party_role="owner_25_plus",
                    requirement="Proof of Address",
                    doc_types=["Proof of Address", "Utility Bill", "Bank Statement"],
                    max_age_months=3,
                    must_be_unexpired=False,
                    must_be_complete=True,
                    must_be_signed=False,
                    description=f"Proof of address dated within 3 months for {name}.",
                ))

    # 3. Trust Client rules
    elif client_type == "trust":
        trust_party = next((p for p in parties if p.get("role") == "trust"), None)
        trust_name = trust_party["name"] if trust_party else "Trust Entity"

        items.append(RequiredItem(
            rule_id="REQ-TRST-01",
            party_name=trust_name,
            party_role="trust",
            requirement="Trust Deed",
            doc_types=["Trust Deed", "Settlement Deed"],
            must_be_unexpired=False,
            must_be_complete=True,
            must_be_signed=True,
            description="Full signed deed of settlement including all execution pages.",
        ))

        for p in parties:
            if p.get("role") == "trustee":
                t_name = p["name"]
                items.append(RequiredItem(
                    rule_id="REQ-TRST-02",
                    party_name=t_name,
                    party_role="trustee",
                    requirement="Trustee Passport / ID",
                    doc_types=["Passport", "National ID"],
                    must_be_unexpired=True,
                    must_be_complete=True,
                    must_be_signed=False,
                    description=f"Identity verification for trustee {t_name}.",
                ))
                items.append(RequiredItem(
                    rule_id="REQ-TRST-03",
                    party_name=t_name,
                    party_role="trustee",
                    requirement="Trustee Proof of Address",
                    doc_types=["Proof of Address", "Utility Bill"],
                    max_age_months=3,
                    must_be_unexpired=False,
                    must_be_complete=True,
                    must_be_signed=False,
                    description=f"Proof of residential address for trustee {t_name}.",
                ))

    return items
