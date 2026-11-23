"""Packaged civil-calendar data generated with Skyfield and JPL DE440s."""

import json
from datetime import timedelta, timezone
from importlib.resources import files

DATA = json.loads(files(__package__).joinpath("almanac.json").read_text(encoding="ascii"))
BEIJING = timezone(timedelta(hours=8))


def beijing_time(dt):
    """Return UTC+8 wall time. Naive datetimes already denote this time."""
    return dt.astimezone(BEIJING).replace(tzinfo=None) if dt.tzinfo is not None else dt
