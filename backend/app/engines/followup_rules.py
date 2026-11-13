from datetime import datetime, date
from typing import Optional, Dict, Any, List
from backend.app.engines.business_calendar import business_days_between, parse_date, format_date

def determine_followup_trigger(
    last_contact_date_str: str,
    current_date_str: str,
    existing_tasks: List[Dict[str, Any]],
    client_name: str,
    rm_name: str
) -> Optional[Dict[str, Any]]:
    """
    Deterministic rule engine for follow-up cadences:
      Day 3 no reply -> task for RM with a pre-drafted reminder
      Day 6          -> task: suggest phone call + talking points
      Day 9          -> flag to RM manager/ops as 'stalled'; contacts nobody
    Enforces:
      - Max one reminder task per case per day
      - Respects active snooze until snoozed_until date
    """
    if not last_contact_date_str:
        return None

    b_days = business_days_between(last_contact_date_str, current_date_str)
    curr_date = parse_date(current_date_str)

    # 1. Enforce snooze rule
    for task in existing_tasks:
        snoozed_until = task.get("snoozed_until")
        if snoozed_until:
            try:
                snooze_dt = parse_date(snoozed_until)
                if curr_date <= snooze_dt and task.get("status") == "snoozed":
                    return None # Still actively snoozed
            except Exception:
                pass

    # 2. Enforce max one reminder task per case per day
    already_triggered_today = any(
        task.get("triggered_at") == current_date_str
        for task in existing_tasks
    )
    if already_triggered_today:
        return None

    # Check which day tiers already exist
    existing_day_numbers = {t.get("day_number") for t in existing_tasks}

    # Day 9 Escalation
    if b_days >= 9 and 9 not in existing_day_numbers:
        return {
            "day_number": 9,
            "task_type": "manager_flag",
            "title": f"Case Stalled (Day 9) - Escalate {client_name} to Operations Manager",
            "pre_drafted_text": (
                f"ACTION FOR RM / OPS MANAGER:\n"
                f"Client '{client_name}' has not responded after 9 business days and 2 reminders.\n"
                f"Under Northgate KYC Policy Section 4.2, the onboarding case is marked STALLED.\n"
                f"No automated client communication will be sent. Escalate to KYC Operations committee."
            ),
            "triggered_at": current_date_str,
            "status": "pending",
        }

    # Day 6 Phone Call Suggestion
    elif b_days >= 6 and 6 not in existing_day_numbers:
        return {
            "day_number": 6,
            "task_type": "phone_call",
            "title": f"Follow-up Phone Call Recommended for {client_name} (Day 6)",
            "pre_drafted_text": (
                f"SUGGESTED TALKING POINTS FOR CALL WITH {client_name.upper()}:\n"
                f"1. Warm check-in on gathering required onboarding documentation.\n"
                f"2. Check if they have questions regarding certified true copies or formats.\n"
                f"3. Note our target completion deadline and offer Northgate courier collection if needed."
            ),
            "triggered_at": current_date_str,
            "status": "pending",
        }

    # Day 3 Email Reminder
    elif b_days >= 3 and 3 not in existing_day_numbers:
        return {
            "day_number": 3,
            "task_type": "email_reminder",
            "title": f"Day 3 Gentle Reminder Due for {client_name}",
            "pre_drafted_text": (
                f"Subject: Following up: Northgate Onboarding Documentation for {client_name}\n\n"
                f"Dear {client_name},\n\n"
                f"I hope you are having a productive week. Following our correspondence on {last_contact_date_str}, "
                f"I am writing with a gentle follow-up regarding the outstanding documentation required for your onboarding.\n\n"
                f"Please let me know if you have any questions or if we can assist in any way.\n\n"
                f"Warm regards,\n{rm_name}\nRelationship Manager, Northgate"
            ),
            "triggered_at": current_date_str,
            "status": "pending",
        }

    return None
