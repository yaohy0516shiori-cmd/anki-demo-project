from datetime import datetime, timezone


def normalize_datetime_value(value):
    """
    Normalize datetime input to one ISO-8601 UTC string format.

    Accept:
    - None
    - datetime object
    - ISO datetime string

    Return:
    - ISO string like 2026-03-30T12:34:56+00:00
    """
    if value is None:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).replace(microsecond=0).isoformat()

    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("datetime string must be valid ISO format")

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat()

    raise TypeError("datetime value must be None, datetime, or ISO datetime string")