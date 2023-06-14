import logging
import re
from datetime import timedelta

logger = logging.getLogger("uvicorn.beiboot")


def convert_to_timedelta(value: str) -> timedelta:
    pattern = re.compile(
        r"((?P<days>-?\d+)d)?((?P<hours>-?\d+)h)?((?P<minutes>-?\d+)m)?((?P<seconds>-?\d+)s)?",
        re.IGNORECASE,
    )
    match = pattern.match(value)
    if not match:
        raise ValueError("Invalid format. Please use the format '1d2h3m4s'")

    parts = {k: int(v) for k, v in match.groupdict().items() if v}
    td = timedelta(**parts)
    if not bool(td):
        ValueError("Invalid format.")

    if td.total_seconds() == 0:
        raise ValueError("Invalid value.")

    return td
