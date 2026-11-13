import pytest
from backend.app.engines.followup_rules import determine_followup_trigger

def test_day_3_reminder_triggers_on_okafor():
    """
    Okafor Family Trust last contact = 9 Nov 2026 (Monday).
    Current simulated date = 12 Nov 2026 (Thursday).
    Business days elapsed = 3.
    Must trigger Day 3 email reminder task!
    """
    trigger = determine_followup_trigger(
        last_contact_date_str="2026-11-09",
        current_date_str="2026-11-12",
        existing_tasks=[],
        client_name="Okafor Family Trust",
        rm_name="Sarah Jenkins"
    )

    assert trigger is not None
    assert trigger["day_number"] == 3
    assert trigger["task_type"] == "email_reminder"
    assert "gentle follow-up" in trigger["pre_drafted_text"].lower() or "reminder" in trigger["pre_drafted_text"].lower()

def test_day_6_suggests_phone_call():
    # 9 Nov + 6 business days = 17 Nov (skipping weekend 14-15 Nov)
    trigger = determine_followup_trigger(
        last_contact_date_str="2026-11-09",
        current_date_str="2026-11-17",
        existing_tasks=[{"day_number": 3, "triggered_at": "2026-11-12"}],
        client_name="Okafor Family Trust",
        rm_name="Sarah Jenkins"
    )

    assert trigger is not None
    assert trigger["day_number"] == 6
    assert trigger["task_type"] == "phone_call"
    assert "talking points" in trigger["pre_drafted_text"].lower()

def test_day_9_flags_manager_and_contacts_nobody():
    # 9 Nov + 9 business days = 20 Nov
    trigger = determine_followup_trigger(
        last_contact_date_str="2026-11-09",
        current_date_str="2026-11-20",
        existing_tasks=[
            {"day_number": 3, "triggered_at": "2026-11-12"},
            {"day_number": 6, "triggered_at": "2026-11-17"}
        ],
        client_name="Okafor Family Trust",
        rm_name="Sarah Jenkins"
    )

    assert trigger is not None
    assert trigger["day_number"] == 9
    assert trigger["task_type"] == "manager_flag"
    assert "stalled" in trigger["title"].lower()
    assert "no automated client communication" in trigger["pre_drafted_text"].lower()

def test_max_one_reminder_per_day_enforced():
    # Task already triggered today
    existing = [{"day_number": 3, "triggered_at": "2026-11-12"}]
    trigger = determine_followup_trigger(
        last_contact_date_str="2026-11-09",
        current_date_str="2026-11-12",
        existing_tasks=existing,
        client_name="Okafor Family Trust",
        rm_name="Sarah Jenkins"
    )
    assert trigger is None

def test_snooze_prevents_firing():
    existing = [
        {
            "day_number": 3,
            "status": "snoozed",
            "snoozed_until": "2026-11-16",
            "triggered_at": "2026-11-12"
        }
    ]
    # Current date is 13 Nov, snoozed until 16 Nov
    trigger = determine_followup_trigger(
        last_contact_date_str="2026-11-09",
        current_date_str="2026-11-13",
        existing_tasks=existing,
        client_name="Okafor Family Trust",
        rm_name="Sarah Jenkins"
    )
    assert trigger is None
