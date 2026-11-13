import pytest
from backend.app.engines.vote_calc import compute_share_and_voting_rights

def test_brightwave_dual_class_voting_rights():
    """
    Company B (Brightwave Software Ltd):
    - Ines Duarte: 600 Class A (1 vote each)
    - Lumen Growth LP: 500 Class B (10 votes each)
    - Kofi Mensah: 400 Class A (1 vote each)
    Total shares = 1500
    Total votes = 600*1 + 500*10 + 400*1 = 6000
    Lumen votes = 5000 / 6000 = 83.33% (with only 33.33% shares!)
    Ines equity = 600 / 1500 = 40.0% (with only 10.0% votes!)
    Kofi equity = 400 / 1500 = 26.67% (with only 6.67% votes!)
    """
    holdings = [
        {"owner": "Ines Duarte", "shares_count": 600, "share_class": "Class A Ordinary", "votes_per_share": 1.0},
        {"owner": "Lumen Growth LP", "shares_count": 500, "share_class": "Class B Ordinary", "votes_per_share": 10.0},
        {"owner": "Kofi Mensah", "shares_count": 400, "share_class": "Class A Ordinary", "votes_per_share": 1.0},
    ]

    res = compute_share_and_voting_rights(holdings)

    assert res.total_shares == 1500
    assert res.total_votes == 6000

    sh_map = {s["owner"]: s for s in res.shareholders}

    lumen = sh_map["Lumen Growth LP"]
    assert lumen["share_pct"] == 33.33
    assert lumen["vote_pct"] == 83.33
    assert lumen["disproportionate_voting"] is True
    assert "(500 shares x 10 votes/share) / 6000 total votes = 83.33%" == lumen["formula_vote"]

    ines = sh_map["Ines Duarte"]
    assert ines["share_pct"] == 40.0
    assert ines["vote_pct"] == 10.0
    assert ines["disproportionate_voting"] is True

    kofi = sh_map["Kofi Mensah"]
    assert kofi["share_pct"] == 26.67
    assert kofi["vote_pct"] == 6.67
