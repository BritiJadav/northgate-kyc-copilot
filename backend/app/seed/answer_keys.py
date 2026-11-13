"""
Answer keys for Module A (3 cases) and Module B (5 companies).
These define the single source of ground truth for evaluations and tests.
"""

# MODULE A ANSWER KEYS
MODULE_A_CASES = [
    {
        "case_number": "CASE-2026-001",
        "client_name": "Priya Raman",
        "client_type": "individual",
        "rm_name": "Sarah Jenkins",
        "rm_email": "s.jenkins@northgate.com",
        "client_email": "priya.raman@example.com",
        "last_contact_date": "2026-11-05",
        "parties": [
            {
                "name": "Priya Raman",
                "role": "individual_client",
                "ownership_pct": 100.0,
                "dob": "1985-06-14",
                "nationality": "British",
            }
        ],
        "expected_gaps": [
            {
                "party_name": "Priya Raman",
                "requirement": "Passport / National ID",
                "status": "EXPIRED",
                "rule_id": "REQ-IND-01",
                "evidence": "Passport expired on 14 Sep 2026 (current date: 12 Nov 2026)",
            },
            {
                "party_name": "Priya Raman",
                "requirement": "Proof of Address",
                "status": "STALE",
                "rule_id": "REQ-IND-02",
                "evidence": "Utility bill dated 30 Jun 2026 is older than 3 months",
            },
            {
                "party_name": "Priya Raman",
                "requirement": "Source of Funds Declaration",
                "status": "MISSING",
                "rule_id": "REQ-IND-03",
                "evidence": "No document received for source of funds declaration",
            },
        ],
        "possible_followons": None,
    },
    {
        "case_number": "CASE-2026-002",
        "client_name": "Harbourline Logistics Ltd",
        "client_type": "company",
        "rm_name": "Marcus Vance",
        "rm_email": "m.vance@northgate.com",
        "client_email": "ops@harbourline-logistics.co.uk",
        "last_contact_date": "2026-11-08",
        "parties": [
            {
                "name": "Harbourline Logistics Ltd",
                "role": "company_entity",
                "ownership_pct": None,
            },
            {
                "name": "Daniel Whitaker",
                "role": "owner_25_plus",
                "ownership_pct": 40.0,
                "dob": "1978-03-22",
                "nationality": "British",
            },
            {
                "name": "Alicia Moreno",
                "role": "owner_25_plus",
                "ownership_pct": 30.0,
                "dob": "1982-11-09",
                "nationality": "Spanish",
            },
            {
                "name": "Robert Cole",
                "role": "director",
                "ownership_pct": 0.0,
                "dob": "1965-07-19",
                "nationality": "British",
            },
        ],
        "expected_gaps": [
            {
                "party_name": "Harbourline Logistics Ltd",
                "requirement": "Register of Members (Shareholders)",
                "status": "MISSING",
                "rule_id": "REQ-CORP-01",
                "evidence": "Certified shareholder register not provided",
            },
            {
                "party_name": "Harbourline Logistics Ltd",
                "requirement": "Bank Statement",
                "status": "INCOMPLETE",
                "rule_id": "REQ-CORP-04",
                "evidence": "Pages 1-2 of 4 received only. Missing pages 3 and 4.",
            },
            {
                "party_name": "Daniel Whitaker",
                "requirement": "Passport / Photo ID",
                "status": "MISSING",
                "rule_id": "REQ-UBO-01",
                "evidence": "Photo ID missing for 40% owner",
            },
            {
                "party_name": "Daniel Whitaker",
                "requirement": "Proof of Address",
                "status": "MISSING",
                "rule_id": "REQ-UBO-02",
                "evidence": "Proof of address missing for 40% owner",
            },
            {
                "party_name": "Alicia Moreno",
                "requirement": "Passport / Photo ID",
                "status": "MISSING",
                "rule_id": "REQ-UBO-01",
                "evidence": "Photo ID missing for 30% owner",
            },
            {
                "party_name": "Alicia Moreno",
                "requirement": "Proof of Address",
                "status": "MISSING",
                "rule_id": "REQ-UBO-02",
                "evidence": "Proof of address missing for 30% owner",
            },
        ],
        "possible_followons": "Shareholder register may reveal an additional beneficial owner holding >= 25% voting or equity interest.",
    },
    {
        "case_number": "CASE-2026-003",
        "client_name": "Okafor Family Trust",
        "client_type": "trust",
        "rm_name": "Sarah Jenkins",
        "rm_email": "s.jenkins@northgate.com",
        "client_email": "trustee@okaforfamilytrust.org",
        "last_contact_date": "2026-11-09", # 3 business days before 12 Nov 2026!
        "parties": [
            {
                "name": "Okafor Family Trust",
                "role": "trust",
                "ownership_pct": None,
            },
            {
                "name": "Emeka Okafor",
                "role": "trustee",
                "ownership_pct": None,
                "dob": "1972-04-18",
                "nationality": "Nigerian",
            },
            {
                "name": "Amara Okafor",
                "role": "settlor",
                "ownership_pct": None,
                "dob": "1948-12-01",
                "nationality": "British",
            },
        ],
        "expected_gaps": [
            {
                "party_name": "Okafor Family Trust",
                "requirement": "Trust Deed",
                "status": "INCOMPLETE",
                "rule_id": "REQ-TRST-01",
                "evidence": "Document ends at page 11 of 12; execution/signature page 12 is missing.",
            },
            {
                "party_name": "Emeka Okafor",
                "requirement": "Trustee Passport / ID",
                "status": "MISSING",
                "rule_id": "REQ-TRST-02",
                "evidence": "Verification of trustee identity not received",
            },
            {
                "party_name": "Emeka Okafor",
                "requirement": "Trustee Proof of Address",
                "status": "MISSING",
                "rule_id": "REQ-TRST-03",
                "evidence": "Proof of residential address for trustee not received",
            },
        ],
        "possible_followons": "Once signature page is received, confirm if protector or named beneficiaries have vested rights.",
    },
]

# MODULE B ANSWER KEYS
MODULE_B_COMPANIES = {
    "COMPANY_A": {
        "name": "Alder & Finch Ltd",
        "code": "COMPANY_A",
        "jurisdiction": "United Kingdom",
        "registration_number": "11892041",
        "incorporation_date": "2021-04-15",
        "files": ["alder_finch_register.pdf"],
        "answer_key": {
            "has_register": True,
            "direct_holdings": [
                {"owner": "Nadia Finch", "shares": 60, "total_shares": 100, "percent": 60.0, "share_class": "Ordinary"},
                {"owner": "Owen Alder", "shares": 40, "total_shares": 100, "percent": 40.0, "share_class": "Ordinary"},
            ],
            "effective_ownership": [
                {"person": "Nadia Finch", "effective_pct": 60.0, "is_ubo": True, "formula": "60.0%"},
                {"person": "Owen Alder", "effective_pct": 40.0, "is_ubo": True, "formula": "40.0%"},
            ],
            "unresolved_pct": 0.0,
            "notes": "Clean register, single tier, simple ownership.",
        },
    },
    "COMPANY_B": {
        "name": "Brightwave Software Ltd",
        "code": "COMPANY_B",
        "jurisdiction": "United Kingdom",
        "registration_number": "13948102",
        "incorporation_date": "2022-09-10",
        "files": ["brightwave_register.pdf", "brightwave_articles.pdf"],
        "answer_key": {
            "has_register": True,
            "total_shares": 1500,
            "total_votes": 6000,
            "direct_holdings": [
                {"owner": "Ines Duarte", "shares": 600, "share_class": "A Ordinary", "votes_per_share": 1, "total_votes": 600, "share_pct": 40.0, "vote_pct": 10.0},
                {"owner": "Lumen Growth LP", "shares": 500, "share_class": "B Ordinary", "votes_per_share": 10, "total_votes": 5000, "share_pct": 33.33, "vote_pct": 83.33},
                {"owner": "Kofi Mensah", "shares": 400, "share_class": "A Ordinary", "votes_per_share": 1, "total_votes": 400, "share_pct": 26.67, "vote_pct": 6.67},
            ],
            "effective_ownership": [
                {"person": "Ines Duarte", "effective_pct": 40.0, "is_ubo": True, "formula": "40.0% equity (10.0% votes)"},
                {"person": "Kofi Mensah", "effective_pct": 26.67, "is_ubo": True, "formula": "26.7% equity (6.7% votes)"},
            ],
            "voting_control": [
                {"entity": "Lumen Growth LP", "vote_pct": 83.33, "formula": "(500 shares * 10 votes) / 6000 total votes = 83.33%"},
            ],
            "unresolved_pct": 33.33,
            "notes": "Two share classes: Class B holds 10 votes per share, giving Lumen Growth LP 83.3% voting power despite 33.3% equity.",
        },
    },
    "COMPANY_C": {
        "name": "Calder Marine Services Ltd",
        "code": "COMPANY_C",
        "jurisdiction": "United Kingdom",
        "registration_number": "09823145",
        "incorporation_date": "2018-03-01",
        "files": ["calder_register_2023.pdf", "calder_stock_transfer_scan.png"],
        "answer_key": {
            "has_register": True,
            "stale_register_date": "2023-05-10",
            "historical_2023": [
                {"owner": "Lars Pedersen", "shares": 150, "percent": 75.0},
                {"owner": "Maya Iyer", "shares": 50, "percent": 25.0},
            ],
            "transfer_event": {
                "transferor": "Lars Pedersen",
                "transferee": "Maya Iyer",
                "shares_transferred": 60,
                "date": "2025-08-02",
            },
            "current_truth": [
                {"person": "Maya Iyer", "shares": 110, "total_shares": 200, "effective_pct": 55.0, "is_ubo": True, "formula": "(50 original + 60 transferred) / 200 = 55.0%"},
                {"person": "Lars Pedersen", "shares": 90, "total_shares": 200, "effective_pct": 45.0, "is_ubo": True, "formula": "(150 original - 60 transferred) / 200 = 45.0%"},
            ],
            "unresolved_pct": 0.0,
            "notes": "Stale 2023 register superseded by August 2025 stock transfer form provided as skewed scan image.",
        },
    },
    "COMPANY_D": {
        "name": "Rowan Bay Consulting Ltd",
        "code": "COMPANY_D",
        "jurisdiction": "United Kingdom",
        "registration_number": "12034981",
        "incorporation_date": "2019-11-20",
        "files": ["rowan_bay_memorandum.pdf", "rowan_bay_articles.pdf"],
        "answer_key": {
            "has_register": False,
            "current_ownership": "NOT_FOUND",
            "memorandum_subscribers": [
                {"person": "Arthur Pendelton", "shares": 1, "as_at": "at incorporation"},
                {"person": "Beatrice Webb", "shares": 1, "as_at": "at incorporation"},
            ],
            "unresolved_pct": 100.0,
            "notes": "NO register provided. All current ownership must be NOT_FOUND. Formation subscribers must be labelled 'at incorporation'.",
        },
    },
    "COMPANY_E": {
        "name": "Kestrel Trading Ltd",
        "code": "COMPANY_E",
        "jurisdiction": "United Kingdom",
        "registration_number": "14829301",
        "incorporation_date": "2023-01-18",
        "files": [
            "kestrel_register.pdf",
            "halden_holdings_register.pdf",
            "norvik_group_register_fr.pdf",
            "pilar_investments_incumbency.pdf",
        ],
        "answer_key": {
            "total_shares": 1000,
            "tier_1_holdings": [
                {"owner": "Halden Holdings B.V.", "shares": 480, "percent": 48.0},
                {"owner": "Pilar Investments Ltd", "shares": 270, "percent": 27.0},
                {"owner": "Samira Qadri", "shares": 150, "percent": 15.0},
                {"owner": "Meridian Nominees Ltd", "shares": 100, "percent": 10.0, "nominee_flag": True},
            ],
            "tier_2_halden": [
                {"owner": "Norvik Group S.A.", "percent": 60.0},
                {"owner": "Tomas Berg", "percent": 40.0, "dob": "1968-04-02"},
            ],
            "tier_3_norvik": [
                {"owner": "Elena Voss", "percent": 50.0},
                {"owner": "Thomas Berg", "percent": 50.0, "dob": "1968-04-02"},
            ],
            "lookthrough_effective": {
                "before_resolution": [
                    {"person": "Tomas Berg", "effective_pct": 19.2, "formula": "48% x 40% = 19.2%"},
                    {"person": "Thomas Berg", "effective_pct": 14.4, "formula": "48% x 60% x 50% = 14.4%"},
                    {"person": "Elena Voss", "effective_pct": 14.4, "formula": "48% x 60% x 50% = 14.4%"},
                    {"person": "Samira Qadri", "effective_pct": 15.0, "formula": "15.0% direct"},
                ],
                "after_resolution_same_person": [
                    {"person": "Thomas / Tomas Berg", "effective_pct": 33.6, "is_ubo": True, "formula": "(48% x 40%) + (48% x 60% x 50%) = 19.2% + 14.4% = 33.6%"},
                    {"person": "Elena Voss", "effective_pct": 14.4, "is_ubo": False, "formula": "48% x 60% x 50% = 14.4%"},
                    {"person": "Samira Qadri", "effective_pct": 15.0, "is_ubo": False, "formula": "15.0% direct"},
                ],
            },
            "unresolved_pct": 37.0, # Pilar (27%) + Meridian (10%)
            "control_flags": [
                {"entity": "Meridian Nominees Ltd", "flag": "nominee", "notes": "Nominee holding with undisclosed owner -> GAP"},
                {"entity": "Wren Fiduciary Ltd", "flag": "trustee_without_beneficiaries", "notes": "Holds Pilar as trustee without named beneficiaries -> GAP"},
            ],
            "candidate_matches": [
                {
                    "person_a": "Tomas Berg",
                    "person_b": "Thomas Berg",
                    "dob": "1968-04-02",
                    "reason": "Name variant (Tomas vs Thomas) with matching Date of Birth (02/04/1968)",
                }
            ],
        },
    },
}
