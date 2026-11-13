from datetime import datetime, date, timedelta
from typing import Union

def parse_date(d: Union[str, date, datetime]) -> date:
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, date):
        return d
    return datetime.strptime(d.strip(), "%Y-%m-%d").date()

def format_date(d: date) -> str:
    return d.strftime("%Y-%m-%d")

def is_business_day(d: Union[str, date]) -> bool:
    dt = parse_date(d)
    # 0 = Monday, ..., 4 = Friday, 5 = Saturday, 6 = Sunday
    return dt.weekday() < 5

def add_business_days(start_date: Union[str, date], n_days: int) -> str:
    """Adds n business days to start_date, skipping weekends."""
    cur = parse_date(start_date)
    added = 0
    while added < n_days:
        cur += timedelta(days=1)
        if cur.weekday() < 5:
            added += 1
    return format_date(cur)

def business_days_between(start_date: Union[str, date], end_date: Union[str, date]) -> int:
    """
    Computes business days elapsed between start_date and end_date (exclusive of start_date, inclusive of end_date).
    If start_date >= end_date, returns 0.
    """
    start = parse_date(start_date)
    end = parse_date(end_date)
    if start >= end:
        return 0

    cur = start + timedelta(days=1)
    business_days = 0
    while cur <= end:
        if cur.weekday() < 5:
            business_days += 1
        cur += timedelta(days=1)
    return business_days
