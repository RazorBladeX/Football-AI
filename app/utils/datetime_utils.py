from datetime import datetime, timezone

import pytz


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def to_local(dt: datetime, tz_name: str = "Europe/London") -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(pytz.timezone(tz_name))


def format_match_time(dt: datetime | None) -> str:
    if not dt:
        return "TBD"
    local_dt = to_local(dt)
    return local_dt.strftime("%d %b %H:%M")
