from backend.app.engines.business_calendar import (
    is_business_day,
    add_business_days,
    business_days_between,
)

def test_is_business_day():
    # 2026-11-12 is Thursday
    assert is_business_day("2026-11-12") is True
    # 2026-11-13 is Friday
    assert is_business_day("2026-11-13") is True
    # 2026-11-14 is Saturday
    assert is_business_day("2026-11-14") is False
    # 2026-11-15 is Sunday
    assert is_business_day("2026-11-15") is False
    # 2026-11-16 is Monday
    assert is_business_day("2026-11-16") is True

def test_add_business_days():
    # Thursday 12 Nov + 1 business day = Friday 13 Nov
    assert add_business_days("2026-11-12", 1) == "2026-11-13"
    # Friday 13 Nov + 1 business day = Monday 16 Nov (skips weekend!)
    assert add_business_days("2026-11-13", 1) == "2026-11-16"
    # Thursday 12 Nov + 3 business days = Tuesday 17 Nov
    assert add_business_days("2026-11-12", 3) == "2026-11-17"

def test_business_days_between():
    # Monday 9 Nov to Thursday 12 Nov = 3 business days
    assert business_days_between("2026-11-09", "2026-11-12") == 3
    # Friday 13 Nov to Monday 16 Nov = 1 business day (weekend skipped)
    assert business_days_between("2026-11-13", "2026-11-16") == 1
    # Same date = 0
    assert business_days_between("2026-11-12", "2026-11-12") == 0
