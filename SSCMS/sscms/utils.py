import re
from datetime import datetime
from typing import Tuple

from sscms.config import DATE_FMT

_PHONE_RE = re.compile(r"^[0-9+\-\s]{7,20}$")


def normalize_ws(s: str) -> str:
    return " ".join(s.strip().split())


def is_valid_phone(phone: str) -> bool:
    return bool(_PHONE_RE.match(phone.strip()))


def is_valid_date(value: str) -> bool:
    try:
        datetime.strptime(value.strip(), DATE_FMT)
        return True
    except ValueError:
        return False


def safe_int(value: str) -> Tuple[bool, int]:
    try:
        return True, int(value)
    except ValueError:
        return False, 0


