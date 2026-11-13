import pytest
from backend.app.engines.lookthrough import compute_lookthrough

def test_kestrel_lookthrough_before_and_after_berg_resolution():
    """
    Company E: Kestrel Trading Ltd (1,000 shares):
    Tier 1:
      - 48% Halden Holdings B.V.
      - 27% Pilar Investments Ltd (held by Wren Fiduciary Ltd as trustee, no beneficiaries)
      - 15% Samira Qadri
      - 10% Meridian Nominees Ltd (as nominee, owner undisclosed)
    Tier 2 (Halden Holdings B.V.):
      - 60% Norvik Group S.A.
      - 40% Tomas Berg (DOB 02/04/1968)
    Tier 3 (Norvik Group S.A.):
      - 50% Elena Voss
      - 50% Thomas Berg (DOB 02/04/1968)

    BEFORE RESOLUTION:
      Tomas Berg = 48% x 40% = 19.2% (< 25%, not a UBO)
      Thomas Berg = 48% x 60% x 50% = 14.4% (< 25%, not a UBO)
      Elena Voss = 48% x 60% x 50% = 14.4%
      Samira Qadri = 15.0%
      Unresolved = 37.0% (Pilar 27% + Meridian 10%)

    AFTER RESOLUTION (Analyst confirms Tomas and Thomas are same person):
      Berg = 19.2% + 14.4% = 33.6% (>= 25%, is a UBO!)
    """
    target = "Kestrel Trading Ltd"
    edges = [
        # Tier 1
        {"owner": "Halden Holdings B.V.", "owned": target, "percentage": 48.0},
        {"owner": "Pilar Investments Ltd", "owned": target, "percentage": 27.0},
        {"owner": "Samira Qadri", "owned": target, "percentage": 15.0},
        {"owner": "Meridian Nominees Ltd", "owned": target, "percentage": 10.0},
        # Tier 2
        {"owner": "Norvik Group S.A.", "owned": "Halden Holdings B.V.", "percentage": 60.0},
        {"owner": "Tomas Berg", "owned": "Halden Holdings B.V.", "percentage": 40.0},
        # Tier 3
        {"owner": "Elena Voss", "owned": "Norvik Group S.A.", "percentage": 50.0},
        {"owner": "Thomas Berg", "owned": "Norvik Group S.A.", "percentage": 50.0},
    ]
    unresolved_entities = {"Pilar Investments Ltd", "Meridian Nominees Ltd"}

    # 1. BEFORE RESOLUTION
    res_before = compute_lookthrough(
        target_company=target,
        edges=edges,
        threshold=25.0,
        merged_aliases={},
        unresolved_entities=unresolved_entities,
    )

    owner_map_before = {o["person"]: o for o in res_before.effective_owners}
    assert "Tomas Berg" in owner_map_before
    assert "Thomas Berg" in owner_map_before

    assert owner_map_before["Tomas Berg"]["effective_pct"] == 19.2
    assert owner_map_before["Tomas Berg"]["is_ubo"] is False

    assert owner_map_before["Thomas Berg"]["effective_pct"] == 14.4
    assert owner_map_before["Thomas Berg"]["is_ubo"] is False

    assert owner_map_before["Elena Voss"]["effective_pct"] == 14.4
    assert owner_map_before["Elena Voss"]["is_ubo"] is False

    assert owner_map_before["Samira Qadri"]["effective_pct"] == 15.0

    # Unresolved = Pilar (27%) + Meridian (10%) = 37%
    assert res_before.unresolved_pct == 37.0
    assert len(res_before.unresolved_holders) == 2

    # 2. AFTER RESOLUTION
    merged_name = "Thomas / Tomas Berg"
    aliases = {
        "Tomas Berg": merged_name,
        "Thomas Berg": merged_name,
    }

    res_after = compute_lookthrough(
        target_company=target,
        edges=edges,
        threshold=25.0,
        merged_aliases=aliases,
        unresolved_entities=unresolved_entities,
    )

    owner_map_after = {o["person"]: o for o in res_after.effective_owners}
    assert merged_name in owner_map_after
    berg = owner_map_after[merged_name]

    # Look-through calculation MUST be exactly 33.6% (19.2% + 14.4%)
    assert berg["effective_pct"] == 33.6
    # Berg crosses the 25% threshold and becomes a Beneficial Owner!
    assert berg["is_ubo"] is True
    assert berg["paths_count"] == 2
    assert "19.20%" in berg["formula"]
    assert "14.40%" in berg["formula"]
    assert "33.60%" in berg["formula"]

def test_lookthrough_cycle_detection():
    # Graph with cycle: A owns B, B owns A
    target = "CycleCorp Ltd"
    edges = [
        {"owner": "HoldCo A", "owned": target, "percentage": 50.0},
        {"owner": "HoldCo B", "owned": "HoldCo A", "percentage": 100.0},
        {"owner": "HoldCo A", "owned": "HoldCo B", "percentage": 100.0}, # Cycle!
    ]
    res = compute_lookthrough(target_company=target, edges=edges)
    assert res.has_cycles is True
    assert len(res.cycles) > 0
