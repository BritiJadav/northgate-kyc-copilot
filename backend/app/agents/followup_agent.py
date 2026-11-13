from typing import Optional, Dict, Any, List
from backend.app.engines.followup_rules import determine_followup_trigger
from backend.app.models.chase import ReminderTask

class FollowUpAgent:
    """
    Follow-up agent that checks contact timelines against business calendar rules
    and triggers Day 3 / 6 / 9 action tasks for the Relationship Manager.
    """
    def __init__(self):
        pass

    def run(
        self,
        last_contact_date_str: str,
        current_date_str: str,
        existing_tasks: List[Dict[str, Any]],
        client_name: str,
        rm_name: str
    ) -> Optional[Dict[str, Any]]:
        return determine_followup_trigger(
            last_contact_date_str=last_contact_date_str,
            current_date_str=current_date_str,
            existing_tasks=existing_tasks,
            client_name=client_name,
            rm_name=rm_name,
        )
