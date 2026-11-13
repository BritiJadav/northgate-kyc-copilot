import os
import hashlib
import json
from pathlib import Path
from backend.app.config import settings
from backend.app.db import SessionLocal, init_db
from backend.app.models.chase import (
    ChaseCase,
    Party,
    RequirementsMatrixRule,
    ReceivedDocument,
)
from backend.app.models.kyc import (
    Company,
    CompanyDocument,
)
from backend.app.models.governance import (
    SimulatedClock,
    AuditLog,
)
from backend.app.seed.pdf_generator import generate_all_seed_files, DATA_DIR
from backend.app.seed.answer_keys import MODULE_A_CASES, MODULE_B_COMPANIES

def compute_file_hash(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def seed_requirements_rules(db):
    """Populates deterministic KYC requirements rules matrix."""
    rules = [
        RequirementsMatrixRule(
            rule_code="REQ-IND-01",
            client_type="individual",
            target_role="individual_client",
            document_type="Passport / National ID",
            max_age_months=None,
            must_be_unexpired=True,
            must_be_complete=True,
            must_be_signed=True,
            description="Valid government-issued photo identity document. Must not be expired.",
        ),
        RequirementsMatrixRule(
            rule_code="REQ-IND-02",
            client_type="individual",
            target_role="individual_client",
            document_type="Proof of Address",
            max_age_months=3,
            must_be_unexpired=False,
            must_be_complete=True,
            must_be_signed=False,
            description="Utility bill or bank statement dated within the last 3 calendar months.",
        ),
        RequirementsMatrixRule(
            rule_code="REQ-IND-03",
            client_type="individual",
            target_role="individual_client",
            document_type="Source of Funds Declaration",
            max_age_months=12,
            must_be_unexpired=False,
            must_be_complete=True,
            must_be_signed=True,
            description="Signed client declaration explaining source of wealth and origin of funds.",
        ),
        RequirementsMatrixRule(
            rule_code="REQ-CORP-01",
            client_type="company",
            target_role="company_entity",
            document_type="Register of Members (Shareholders)",
            max_age_months=None,
            must_be_unexpired=False,
            must_be_complete=True,
            must_be_signed=True,
            description="Certified register of shareholders detailing all holdings and share classes.",
        ),
        RequirementsMatrixRule(
            rule_code="REQ-CORP-02",
            client_type="company",
            target_role="company_entity",
            document_type="Certificate of Incorporation",
            max_age_months=None,
            must_be_unexpired=False,
            must_be_complete=True,
            must_be_signed=False,
            description="Official certificate of registration from Companies Registry.",
        ),
        RequirementsMatrixRule(
            rule_code="REQ-CORP-03",
            client_type="company",
            target_role="company_entity",
            document_type="Articles of Association",
            max_age_months=None,
            must_be_unexpired=False,
            must_be_complete=True,
            must_be_signed=False,
            description="Articles and constitution defining company regulations and share rights.",
        ),
        RequirementsMatrixRule(
            rule_code="REQ-CORP-04",
            client_type="company",
            target_role="company_entity",
            document_type="Bank Statement",
            max_age_months=3,
            must_be_unexpired=False,
            must_be_complete=True,
            must_be_signed=False,
            description="Corporate bank account statement for the most recent period; all pages required.",
        ),
        RequirementsMatrixRule(
            rule_code="REQ-UBO-01",
            client_type="all",
            target_role="owner_25_plus",
            document_type="Passport / Photo ID",
            max_age_months=None,
            must_be_unexpired=True,
            must_be_complete=True,
            must_be_signed=False,
            description="Government-issued photo ID for any ultimate beneficial owner holding >= 25%.",
        ),
        RequirementsMatrixRule(
            rule_code="REQ-UBO-02",
            client_type="all",
            target_role="owner_25_plus",
            document_type="Proof of Address",
            max_age_months=3,
            must_be_unexpired=False,
            must_be_complete=True,
            must_be_signed=False,
            description="Proof of residential address dated within 3 months for beneficial owner >= 25%.",
        ),
        RequirementsMatrixRule(
            rule_code="REQ-TRST-01",
            client_type="trust",
            target_role="trust",
            document_type="Trust Deed",
            max_age_months=None,
            must_be_unexpired=False,
            must_be_complete=True,
            must_be_signed=True,
            description="Complete signed deed of settlement including all schedules and execution pages.",
        ),
        RequirementsMatrixRule(
            rule_code="REQ-TRST-02",
            client_type="trust",
            target_role="trustee",
            document_type="Trustee Passport / ID",
            max_age_months=None,
            must_be_unexpired=True,
            must_be_complete=True,
            must_be_signed=False,
            description="Proof of identity for all appointed trustees.",
        ),
        RequirementsMatrixRule(
            rule_code="REQ-TRST-03",
            client_type="trust",
            target_role="trustee",
            document_type="Trustee Proof of Address",
            max_age_months=3,
            must_be_unexpired=False,
            must_be_complete=True,
            must_be_signed=False,
            description="Residential address verification for trustees dated within 3 months.",
        ),
    ]
    for r in rules:
        db.add(r)
    db.commit()

def seed_module_a_cases(db):
    """Seeds the 3 Module A test cases."""
    # Case 1: Priya Raman
    c1_data = MODULE_A_CASES[0]
    case1 = ChaseCase(
        case_number=c1_data["case_number"],
        client_name=c1_data["client_name"],
        client_type=c1_data["client_type"],
        status="in_progress",
        rm_name=c1_data["rm_name"],
        rm_email=c1_data["rm_email"],
        client_email=c1_data["client_email"],
        last_contact_date=c1_data["last_contact_date"],
        deadline="2026-11-20",
        rounds_count=1,
    )
    db.add(case1)
    db.flush()

    p_raman = Party(
        case_id=case1.id,
        name="Priya Raman",
        role="individual_client",
        ownership_pct=100.0,
        dob="1985-06-14",
        nationality="British",
    )
    db.add(p_raman)
    db.flush()

    # Documents received for Priya Raman
    db.add(ReceivedDocument(
        case_id=case1.id,
        party_id=p_raman.id,
        filename="priya_raman_passport.pdf",
        file_path=str(DATA_DIR / "priya_raman_passport.pdf"),
        doc_type="Passport",
        party_name="Priya Raman",
        issue_date="2016-09-15",
        expiry_date="2026-09-14",
        page_count=1,
        pages_present="1 of 1",
        signed=True,
    ))
    db.add(ReceivedDocument(
        case_id=case1.id,
        party_id=p_raman.id,
        filename="priya_raman_utility_bill.pdf",
        file_path=str(DATA_DIR / "priya_raman_utility_bill.pdf"),
        doc_type="Proof of Address",
        party_name="Priya Raman",
        issue_date="2026-06-30",
        expiry_date=None,
        page_count=1,
        pages_present="1 of 1",
        signed=False,
    ))

    # Case 2: Harbourline Logistics Ltd
    c2_data = MODULE_A_CASES[1]
    case2 = ChaseCase(
        case_number=c2_data["case_number"],
        client_name=c2_data["client_name"],
        client_type=c2_data["client_type"],
        status="in_progress",
        rm_name=c2_data["rm_name"],
        rm_email=c2_data["rm_email"],
        client_email=c2_data["client_email"],
        last_contact_date=c2_data["last_contact_date"],
        deadline="2026-11-23",
        rounds_count=1,
    )
    db.add(case2)
    db.flush()

    for p in c2_data["parties"]:
        db.add(Party(
            case_id=case2.id,
            name=p["name"],
            role=p["role"],
            ownership_pct=p.get("ownership_pct"),
            dob=p.get("dob"),
            nationality=p.get("nationality"),
        ))
    db.flush()

    db.add(ReceivedDocument(
        case_id=case2.id,
        party_id=None,
        filename="harbourline_incorp_cert.pdf",
        file_path=str(DATA_DIR / "harbourline_incorp_cert.pdf"),
        doc_type="Certificate of Incorporation",
        party_name="Harbourline Logistics Ltd",
        issue_date="2017-02-14",
        page_count=1,
        pages_present="1 of 1",
        signed=True,
    ))
    db.add(ReceivedDocument(
        case_id=case2.id,
        party_id=None,
        filename="harbourline_bank_statement.pdf",
        file_path=str(DATA_DIR / "harbourline_bank_statement.pdf"),
        doc_type="Bank Statement",
        party_name="Harbourline Logistics Ltd",
        issue_date="2026-10-31",
        page_count=4,
        pages_present="1-2 of 4",
        signed=False,
    ))

    # Case 3: Okafor Family Trust
    c3_data = MODULE_A_CASES[2]
    case3 = ChaseCase(
        case_number=c3_data["case_number"],
        client_name=c3_data["client_name"],
        client_type=c3_data["client_type"],
        status="awaiting_docs",
        rm_name=c3_data["rm_name"],
        rm_email=c3_data["rm_email"],
        client_email=c3_data["client_email"],
        last_contact_date=c3_data["last_contact_date"], # 2026-11-09 -> Day 3 reminder due on 2026-11-12!
        deadline="2026-11-24",
        rounds_count=1,
    )
    db.add(case3)
    db.flush()

    for p in c3_data["parties"]:
        db.add(Party(
            case_id=case3.id,
            name=p["name"],
            role=p["role"],
            ownership_pct=p.get("ownership_pct"),
            dob=p.get("dob"),
            nationality=p.get("nationality"),
        ))
    db.flush()

    db.add(ReceivedDocument(
        case_id=case3.id,
        party_id=None,
        filename="okafor_trust_deed.pdf",
        file_path=str(DATA_DIR / "okafor_trust_deed.pdf"),
        doc_type="Trust Deed",
        party_name="Okafor Family Trust",
        issue_date="2015-11-15",
        page_count=12,
        pages_present="1-11 of 12",
        signed=False,
    ))

    db.commit()

def seed_module_b_companies(db):
    """Seeds the 5 Module B test companies and registers their documents."""
    for code, info in MODULE_B_COMPANIES.items():
        comp = Company(
            code=code,
            name=info["name"],
            jurisdiction=info["jurisdiction"],
            registration_number=info["registration_number"],
            incorporation_date=info["incorporation_date"],
            status="pending_review",
        )
        db.add(comp)
        db.flush()

        for filename in info["files"]:
            file_path = DATA_DIR / filename
            if file_path.exists():
                doc_hash = compute_file_hash(file_path)
                is_scan = filename.endswith(".png")
                page_count = 1 if is_scan else 1 # default
                db.add(CompanyDocument(
                    company_id=comp.id,
                    filename=filename,
                    file_path=str(file_path),
                    doc_hash=doc_hash,
                    page_count=page_count,
                    low_legibility=is_scan, # Scanned transfer form marked low_legibility
                ))
    db.commit()

def seed_simulated_clock(db):
    """Initializes simulated business clock."""
    existing = db.query(SimulatedClock).first()
    if not existing:
        clock = SimulatedClock(current_simulated_date=settings.SIMULATED_DATE)
        db.add(clock)
    else:
        existing.current_simulated_date = settings.SIMULATED_DATE
    db.commit()

def seed_demo_cache_file():
    """Seeds baseline demo cache entries for resilient offline demo execution (C12)."""
    cache_path = Path(__file__).resolve().parent.parent / "demo_cache" / "seed_cache.json"
    os.makedirs(cache_path.parent, exist_ok=True)

    cache_entries = {
        # Classifier cache fallbacks
        "DocClassifierAgent_priya_raman_passport.pdf": {
            "doc_type": "Passport",
            "party_name": "Priya Raman",
            "issue_date": "2016-09-15",
            "expiry_date": "2026-09-14",
            "page_count": 1,
            "pages_present": "1 of 1",
            "signed": True,
        },
        "DocClassifierAgent_priya_raman_utility_bill.pdf": {
            "doc_type": "Proof of Address",
            "party_name": "Priya Raman",
            "issue_date": "2026-06-30",
            "expiry_date": None,
            "page_count": 1,
            "pages_present": "1 of 1",
            "signed": False,
        },
        "DocClassifierAgent_harbourline_bank_statement.pdf": {
            "doc_type": "Bank Statement",
            "party_name": "Harbourline Logistics Ltd",
            "issue_date": "2026-10-31",
            "expiry_date": None,
            "page_count": 4,
            "pages_present": "1-2 of 4",
            "signed": False,
        },
        "DocClassifierAgent_okafor_trust_deed.pdf": {
            "doc_type": "Trust Deed",
            "party_name": "Okafor Family Trust",
            "issue_date": "2015-11-15",
            "expiry_date": None,
            "page_count": 12,
            "pages_present": "1-11 of 12",
            "signed": False,
        },
        # Email Drafter fallbacks
        "EmailDrafterAgent_1": {
            "subject": "Northgate KYC Onboarding: Outstanding Documentation Required for Priya Raman",
            "body": "Dear Priya,\n\nThank you for choosing Northgate. We are pleased to assist you with onboarding. To proceed with setting up your account, we require the following outstanding documentation by [RM TO CONFIRM: deadline]:\n\n1. Passport / National ID: The passport provided expired on 14 September 2026. Please supply a certified copy of your current, unexpired passport.\n2. Proof of Address: The water utility bill dated 30 June 2026 exceeds our 3-month validity limit. Please provide a utility bill or bank statement dated within the last 3 months.\n3. Source of Funds Declaration: Please complete and return our standard source of funds declaration form.\n\nPlease reply directly to this email with the requested documents attached.\n\nWarm regards,\nSarah Jenkins\nRelationship Manager, Northgate",
            "notes_for_rm": "Client's passport expired recently. Water bill was dated June 2026. Standard 3-month recency rule applies.",
            "possible_followons": None,
        },
        # Company Extractor cache fallbacks
        "OwnershipExtractorAgent_COMPANY_A": {
            "edges": [
                {
                    "owner": "Nadia Finch",
                    "owned": "Alder & Finch Ltd",
                    "shares_count": 60,
                    "percentage": 60.0,
                    "share_class": "Ordinary",
                    "votes_per_share": 1.0,
                    "as_at_date": "current",
                    "doc": "alder_finch_register.pdf",
                    "page": 1,
                    "line": 7,
                    "verbatim_quote": "Shares Held: 60 Ordinary Shares (Certificate #AF-001)",
                },
                {
                    "owner": "Owen Alder",
                    "owned": "Alder & Finch Ltd",
                    "shares_count": 40,
                    "percentage": 40.0,
                    "share_class": "Ordinary",
                    "votes_per_share": 1.0,
                    "as_at_date": "current",
                    "doc": "alder_finch_register.pdf",
                    "page": 1,
                    "line": 12,
                    "verbatim_quote": "Shares Held: 40 Ordinary Shares (Certificate #AF-002)",
                },
            ],
            "officers": [
                {"name": "Nadia Finch", "role": "Director", "doc": "alder_finch_register.pdf", "page": 1, "line": 16, "verbatim_quote": "Director: Nadia Finch (Appointed 15 April 2021)"},
                {"name": "Owen Alder", "role": "Director", "doc": "alder_finch_register.pdf", "page": 1, "line": 17, "verbatim_quote": "Director: Owen Alder (Appointed 15 April 2021)"},
            ],
            "entity_facts": ["Issued Capital: 100 Ordinary Shares of £1.00 each"],
            "has_share_register": True,
            "notes": "Single tier ownership register.",
        },
        "OwnershipExtractorAgent_COMPANY_B": {
            "edges": [
                {
                    "owner": "Ines Duarte",
                    "owned": "Brightwave Software Ltd",
                    "shares_count": 600,
                    "percentage": 40.0,
                    "share_class": "Class A Ordinary",
                    "votes_per_share": 1.0,
                    "as_at_date": "current",
                    "doc": "brightwave_register.pdf",
                    "page": 1,
                    "line": 7,
                    "verbatim_quote": "Number of Shares: 600",
                },
                {
                    "owner": "Lumen Growth LP",
                    "owned": "Brightwave Software Ltd",
                    "shares_count": 500,
                    "percentage": 33.33,
                    "share_class": "Class B Ordinary",
                    "votes_per_share": 10.0,
                    "as_at_date": "current",
                    "doc": "brightwave_register.pdf",
                    "page": 1,
                    "line": 13,
                    "verbatim_quote": "Number of Shares: 500",
                },
                {
                    "owner": "Kofi Mensah",
                    "owned": "Brightwave Software Ltd",
                    "shares_count": 400,
                    "percentage": 26.67,
                    "share_class": "Class A Ordinary",
                    "votes_per_share": 1.0,
                    "as_at_date": "current",
                    "doc": "brightwave_register.pdf",
                    "page": 1,
                    "line": 19,
                    "verbatim_quote": "Number of Shares: 400",
                },
            ],
            "officers": [],
            "entity_facts": ["Two share classes: Class A (1 vote), Class B (10 votes)"],
            "has_share_register": True,
            "notes": "Articles specify 10 votes per share for Class B.",
        },
        "OwnershipExtractorAgent_COMPANY_C": {
            "edges": [
                {
                    "owner": "Maya Iyer",
                    "owned": "Calder Marine Services Ltd",
                    "shares_count": 110,
                    "percentage": 55.0,
                    "share_class": "Ordinary",
                    "votes_per_share": 1.0,
                    "as_at_date": "2025-08-02",
                    "doc": "calder_stock_transfer_scan.png",
                    "page": 1,
                    "line": 14,
                    "verbatim_quote": "Maya Iyer 110 shares (55%)",
                },
                {
                    "owner": "Lars Pedersen",
                    "owned": "Calder Marine Services Ltd",
                    "shares_count": 90,
                    "percentage": 45.0,
                    "share_class": "Ordinary",
                    "votes_per_share": 1.0,
                    "as_at_date": "2025-08-02",
                    "doc": "calder_stock_transfer_scan.png",
                    "page": 1,
                    "line": 14,
                    "verbatim_quote": "Lars Pedersen 90 shares (45%)",
                },
            ],
            "officers": [],
            "entity_facts": ["Transfer of 60 shares on 02 August 2025 from Lars Pedersen to Maya Iyer"],
            "has_share_register": True,
            "notes": "Transfer form supersedes 2023 historical register.",
        },
        "OwnershipExtractorAgent_COMPANY_D": {
            "edges": [],
            "officers": [],
            "entity_facts": ["Formation memorandum from 20 November 2019 only", "No share register provided"],
            "has_share_register": False,
            "notes": "Only formation memorandum exists. Current ownership NOT_FOUND.",
        },
        "OwnershipExtractorAgent_COMPANY_E": {
            "edges": [
                {
                    "owner": "Halden Holdings B.V.",
                    "owned": "Kestrel Trading Ltd",
                    "shares_count": 480,
                    "percentage": 48.0,
                    "share_class": "Ordinary",
                    "votes_per_share": 1.0,
                    "as_at_date": "current",
                    "doc": "kestrel_register.pdf",
                    "page": 1,
                    "line": 7,
                    "verbatim_quote": "Shares Held: 480 Ordinary Shares (48.0% of total issued equity)",
                },
                {
                    "owner": "Pilar Investments Ltd",
                    "owned": "Kestrel Trading Ltd",
                    "shares_count": 270,
                    "percentage": 27.0,
                    "share_class": "Ordinary",
                    "votes_per_share": 1.0,
                    "as_at_date": "current",
                    "doc": "kestrel_register.pdf",
                    "page": 1,
                    "line": 11,
                    "verbatim_quote": "Shares Held: 270 Ordinary Shares (27.0% of total issued equity)",
                },
                {
                    "owner": "Samira Qadri",
                    "owned": "Kestrel Trading Ltd",
                    "shares_count": 150,
                    "percentage": 15.0,
                    "share_class": "Ordinary",
                    "votes_per_share": 1.0,
                    "as_at_date": "current",
                    "doc": "kestrel_register.pdf",
                    "page": 1,
                    "line": 15,
                    "verbatim_quote": "Shares Held: 150 Ordinary Shares (15.0% of total issued equity)",
                },
                {
                    "owner": "Meridian Nominees Ltd",
                    "owned": "Kestrel Trading Ltd",
                    "shares_count": 100,
                    "percentage": 10.0,
                    "share_class": "Ordinary",
                    "votes_per_share": 1.0,
                    "as_at_date": "current",
                    "doc": "kestrel_register.pdf",
                    "page": 1,
                    "line": 19,
                    "verbatim_quote": "Shares Held: 100 Ordinary Shares (10.0% of total issued equity)",
                },
                # Tier 2: Halden Holdings B.V.
                {
                    "owner": "Norvik Group S.A.",
                    "owned": "Halden Holdings B.V.",
                    "shares_count": None,
                    "percentage": 60.0,
                    "share_class": "Ordinary",
                    "votes_per_share": 1.0,
                    "as_at_date": "current",
                    "doc": "halden_holdings_register.pdf",
                    "page": 1,
                    "line": 8,
                    "verbatim_quote": "Aandelenbezit: 60% van het geplaatste kapitaal (60.0% interest)",
                },
                {
                    "owner": "Tomas Berg",
                    "owned": "Halden Holdings B.V.",
                    "shares_count": None,
                    "percentage": 40.0,
                    "share_class": "Ordinary",
                    "votes_per_share": 1.0,
                    "as_at_date": "current",
                    "doc": "halden_holdings_register.pdf",
                    "page": 1,
                    "line": 14,
                    "verbatim_quote": "Aandelenbezit: 40% van het geplaatste kapitaal (40.0% interest)",
                },
                # Tier 3: Norvik Group S.A.
                {
                    "owner": "Elena Voss",
                    "owned": "Norvik Group S.A.",
                    "shares_count": 50,
                    "percentage": 50.0,
                    "share_class": "Ordinary",
                    "votes_per_share": 1.0,
                    "as_at_date": "current",
                    "doc": "norvik_group_register_fr.pdf",
                    "page": 1,
                    "line": 8,
                    "verbatim_quote": "Actions détenues: 50 actions ordinaires (50.0% du capital social)",
                },
                {
                    "owner": "Thomas Berg",
                    "owned": "Norvik Group S.A.",
                    "shares_count": 50,
                    "percentage": 50.0,
                    "share_class": "Ordinary",
                    "votes_per_share": 1.0,
                    "as_at_date": "current",
                    "doc": "norvik_group_register_fr.pdf",
                    "page": 1,
                    "line": 14,
                    "verbatim_quote": "Actions détenues: 50 actions ordinaires (50.0% du capital social)",
                },
            ],
            "officers": [
                {"name": "Samira Qadri", "role": "Director", "doc": "kestrel_register.pdf", "page": 1, "line": 23, "verbatim_quote": "Director: Samira Qadri (Appointed 18 January 2023)"},
                {"name": "Tomas Berg", "role": "Director", "doc": "halden_holdings_register.pdf", "page": 1, "line": 16, "verbatim_quote": "Bestuurder: Tomas Berg."},
            ],
            "entity_facts": ["Tier 1 UK Company", "Tier 2 Dutch B.V.", "Tier 3 Luxembourg S.A.", "BVI Trustee Holding"],
            "has_share_register": True,
            "notes": "Multi-tier holding structure with French and Dutch corporate records.",
        },
    }

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache_entries, f, indent=2)

def seed_all(generate_files: bool = True):
    """Wipes and seeds the entire database from scratch, generating files and cache."""
    if generate_files or not (DATA_DIR / "master_text_layers.json").exists():
        print("1. Generating synthetic document files...")
        generate_all_seed_files()
    else:
        print("1. Synthetic document files already exist, skipping regeneration.")

    print("2. Initializing SQLite tables...")
    init_db()

    db = SessionLocal()
    try:
        # Clear existing rows to be idempotent
        from backend.app.models.chase import (
            ChaseCase, Party, RequirementsMatrixRule, ReceivedDocument, GapRow, ChaseEmail, ReminderTask
        )
        from backend.app.models.kyc import (
            Company, CompanyDocument, AISuggestion, PossibleMatch, AnalystDecision, ConfirmedRecord
        )
        from backend.app.models.governance import AuditLog, AgentRun, MetricsEvent, SimulatedClock

        db.query(ConfirmedRecord).delete()
        db.query(AnalystDecision).delete()
        db.query(PossibleMatch).delete()
        db.query(AISuggestion).delete()
        db.query(CompanyDocument).delete()
        db.query(Company).delete()

        db.query(ReminderTask).delete()
        db.query(ChaseEmail).delete()
        db.query(GapRow).delete()
        db.query(ReceivedDocument).delete()
        db.query(Party).delete()
        db.query(RequirementsMatrixRule).delete()
        db.query(ChaseCase).delete()

        db.query(AuditLog).delete()
        db.query(AgentRun).delete()
        db.query(MetricsEvent).delete()
        db.commit()

        print("3. Seeding requirements rules...")
        seed_requirements_rules(db)

        print("4. Seeding Module A chase cases...")
        seed_module_a_cases(db)

        print("5. Seeding Module B companies...")
        seed_module_b_companies(db)

        print("6. Initializing simulated clock...")
        seed_simulated_clock(db)

        print("7. Seeding demo cache entries...")
        seed_demo_cache_file()

        print("Database seeded successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_all()
